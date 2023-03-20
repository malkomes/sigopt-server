/**
 * Copyright © 2022 Intel Corporation
 *
 * SPDX-License-Identifier: Apache License 2.0
 */

// auto-generated via ./web/js/component/glyph/support_glyph.sh up-right-and-down-left-from-center

import "./glyph.less";

import React from "react";

import Glyph from "../base";

const glyphName = "up-right-and-down-left-from-center";
export default class extends React.Component {
  static displayName = `Glyph(${glyphName})`;
  static glyphName = glyphName;

  render() {
    return <Glyph {...this.props} glyph={glyphName} />;
  }
}
