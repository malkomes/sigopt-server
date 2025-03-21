/**
 * Copyright © 2022 Intel Corporation
 *
 * SPDX-License-Identifier: Apache License 2.0
 */

import _ from "underscore";
import cluster from "cluster";
import path from "path";
import {program} from "commander";

import ConfigBroker from "../config/broker";
import GlobalServiceBag from "../services/global";
import makeApp from "./express/app";
import {ENTRY_MANIFEST_FILE_NAME} from "../webpack/constants";

/* eslint-disable no-console */

export default function main() {
  const opts = program
    .option("--workers [n]", "How many worker processes to run")
    .parse(process.argv);
  process.on("unhandledRejection", (reason, p) => {
    console.error("Unhandled Rejection at:", p, "reason:", reason);
    process.exit(1);
  });

  process.on("uncaughtException", (err) => {
    console.error("Uncaught exception:", err);
    process.exit(1);
  });

  const scriptPath = process.argv[1];
  const entryManifestFile = path.join(
    path.dirname(scriptPath),
    ENTRY_MANIFEST_FILE_NAME,
  );

  if (process.env.NODE_ENV === "production" && cluster.isMaster) {
    _.each(_.range(opts.workers || 1), () => cluster.fork());
    return Promise.resolve(null);
  }
  const configBroker = ConfigBroker.fromFile(
    process.env.sigopt_server_config_file,
  );
  return new Promise((s, e) => configBroker.initialize(s, e))
    .then(() => {
      const globalServiceBag = new GlobalServiceBag(
        configBroker,
        entryManifestFile,
      );
      return globalServiceBag.warmup();
    })
    .then((globalServiceBag) => {
      const nodePort = configBroker.get("express.port", 4000);
      const app = makeApp(globalServiceBag);
      const server = app.listen(nodePort);
      server.keepAliveTimeout = 75 * 1000;
      server.headersTimeout = 75 * 1000;
      return {app, server};
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
