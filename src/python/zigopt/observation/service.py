# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0
from sqlalchemy import case, desc, func

from zigopt.common import *
from zigopt.common.sigopt_datetime import current_datetime, datetime_to_seconds
from zigopt.common.struct import ImmutableStruct
from zigopt.db.util import DeleteClause
from zigopt.observation.data import *
from zigopt.observation.model import Observation
from zigopt.profile.timing import *
from zigopt.services.base import Service


ObservationCounts = ImmutableStruct(
  "ObservationCounts",
  (
    "failure_count",
    "observation_count",
    "max_observation_id",
  ),
)


class ObservationService(Service):
  def validate_assignments_present(self, experiment, observations):
    for observation in observations:
      if observation.get_assignments(experiment) is None:
        raise ValueError("Cannot create an observation without assignments")
    return True

  def find_by_id(self, observation_id, include_deleted=False):
    return list_get(self.find_by_ids([observation_id], include_deleted), 0)

  def find_by_ids(self, observation_ids, include_deleted=False):
    if len(observation_ids) == 0:
      return []

    return self.services.database_service.all(
      self._include_deleted_clause_deprecated(
        include_deleted, self.services.database_service.query(Observation).filter(Observation.id.in_(observation_ids))
      )
    )

  def find_by_processed_suggestion_ids(self, processed_suggestion_ids, include_deleted=False):
    if len(processed_suggestion_ids) == 0:
      return []

    return self.services.database_service.all(
      self._include_deleted_clause_deprecated(
        include_deleted,
        self.services.database_service.query(Observation).filter(
          Observation.processed_suggestion_id.in_(processed_suggestion_ids)
        ),
      )
    )

  def read(self, experiment_id, limit, before, after, ascending=False, deleted=DeleteClause.NOT_DELETED):
    return self.services.query_pager.get_page_results(
      self._include_deleted_clause(
        deleted, self.services.database_service.query(Observation).filter(Observation.experiment_id == experiment_id)
      ),
      Observation.id,
      limit=limit,
      before=before,
      after=after,
      ascending=ascending,
    )

  def all_data(self, experiment, include_deleted=False):
    return self.all_data_for_experiments([experiment], include_deleted)

  def all_data_for_experiments(self, experiments, include_deleted=False):
    """
        Returns observations for this experiment.

        :return: all observations associated with the specified experiment
        :rtype: list of ``sigopt.observation.point.Observation``
        """
    if not experiments:
      return []

    experiment_ids = [e.id for e in experiments]
    return self.services.database_service.all(
      self._include_deleted_clause_deprecated(
        include_deleted,
        self.services.database_service.query(Observation).filter(Observation.experiment_id.in_(experiment_ids)),
      ).order_by(desc(Observation.id))
    )

  @time_function("sigopt.timing", log_attributes=lambda self, experiment: {"experiment": str(experiment.id)})
  def last_observation(self, experiment):
    return self.services.database_service.first(
      self.services.database_service.query(Observation)
      .filter_by(experiment_id=experiment.id)
      .order_by(desc(Observation.id))
    )

  def count_by_experiment(
    self,
    experiment,
    limit=None,
    deleted=DeleteClause.NOT_DELETED,
    after=None,
  ):
    """
        :param limit: Adds a limit to the count. Useful if you only want to
          know if the count is greater than some threshold.
        :return: number of observations for this experiment
        :rtype: int
        """
    q = self.services.database_service.query(Observation).filter(Observation.experiment_id == experiment.id)
    if after is not None:
      q = q.filter(Observation.id > after)
    q = self._include_deleted_clause(deleted, q)
    if limit is not None:
      q = q.limit(limit)
    return self.services.database_service.count(q)

  # TODO - Allow to include deleted observations
  def get_observation_counts(self, experiment_id):
    failure_count, observation_count, max_observation_id = self.services.database_service.one_or_none(
      self.services.database_service.query(
        func.sum(case([(Observation.data.reported_failure.as_boolean(), 1)], else_=0)),
        func.count(Observation.id),
        func.max(Observation.id),
      )
      .filter(~Observation.data.deleted.as_boolean())
      .filter(Observation.experiment_id == experiment_id)
      .group_by(Observation.experiment_id)
    ) or (0, 0, 0)
    return ObservationCounts(
      failure_count=failure_count,
      observation_count=observation_count,
      max_observation_id=max_observation_id,
    )

  def valid_observations(self, observations, cost=None):
    return [o for o in observations if o.reported_failure is not True and (cost is None or o.data.task.cost == cost)]

  def find_valid_observations(self, experiment):
    return self.services.database_service.all(
      self.services.database_service.query(Observation)
      .filter(~Observation.data.deleted.as_boolean())
      .filter(~Observation.data.reported_failure.as_boolean())
      .filter(Observation.experiment_id == experiment.id)
    )

  def latest_observation_id(self, experiment_id):
    obs = self.latest_observation(experiment_id)
    return obs and obs.id

  def latest_observation(self, experiment_id, include_deleted=False):
    return self.services.database_service.first(
      self._include_deleted_clause_deprecated(
        include_deleted,
        self.services.database_service.query(Observation).filter(Observation.experiment_id == experiment_id),
      ).order_by(desc(Observation.id))
    )

  def set_delete(self, experiment, observation_id, deleted=True):
    now = current_datetime()
    observation = self.find_by_id(observation_id, include_deleted=True)
    new_data = observation.data.copy_protobuf()
    new_data.deleted = deleted
    new_data.timestamp = datetime_to_seconds(now)
    self.services.database_service.update_one(
      self.services.database_service.query(Observation).filter(Observation.id == observation_id),
      {Observation.data: new_data},
    )
    self.services.experiment_service.mark_as_updated(experiment, now)

  def delete_all_for_experiment(self, experiment):
    now = current_datetime()
    updated_observations = []
    for old_observation in self.services.database_service.all(
      self._include_deleted_clause_deprecated(
        False,
        self.services.database_service.query(Observation).filter(Observation.experiment_id == experiment.id),
      )
    ):
      new_observation = old_observation.data.copy_protobuf()
      new_observation.deleted = True
      new_observation.timestamp = datetime_to_seconds(now)
      updated_observations.append({"id": old_observation.id, "data": new_observation})
    self.services.database_service.update_all(Observation, updated_observations)
    self.services.experiment_service.mark_as_updated(experiment, now)

  def insert_observations(self, experiment, observations):
    self.validate_assignments_present(experiment, observations)
    self.services.database_service.insert_all(observations)

  def optimize(
    self,
    experiment,
    num_observations,
    should_enqueue_hyper_opt=True,
  ):
    if not experiment.development and experiment.should_offline_optimize:
      self.services.optimize_queue_service.enqueue_optimization(
        experiment,
        should_enqueue_hyper_opt=should_enqueue_hyper_opt,
        num_observations=num_observations,
      )

  def _include_deleted_clause_deprecated(self, include_deleted, q):
    if not include_deleted:
      return q.filter(~Observation.data.deleted.as_boolean())
    return q

  def _include_deleted_clause(self, deleted, q):
    if deleted is DeleteClause.NOT_DELETED:
      return q.filter(~Observation.data.deleted.as_boolean())
    if deleted is DeleteClause.DELETED:
      return q.filter(Observation.data.deleted.as_boolean())
    assert deleted is DeleteClause.ALL
    return q
