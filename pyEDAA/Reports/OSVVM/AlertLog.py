# ==================================================================================================================== #
#              _____ ____    _        _      ____                       _                                              #
#  _ __  _   _| ____|  _ \  / \      / \    |  _ \ ___ _ __   ___  _ __| |_ ___                                        #
# | '_ \| | | |  _| | | | |/ _ \    / _ \   | |_) / _ \ '_ \ / _ \| '__| __/ __|                                       #
# | |_) | |_| | |___| |_| / ___ \  / ___ \ _|  _ <  __/ |_) | (_) | |  | |_\__ \                                       #
# | .__/ \__, |_____|____/_/   \_\/_/   \_(_)_| \_\___| .__/ \___/|_|   \__|___/                                       #
# |_|    |___/                                        |_|                                                              #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2021-2024 Electronic Design Automation Abstraction (EDA²)                                                  #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""A data model for OSVVM's AlertLog YAML file format."""
from datetime import timedelta
from enum     import Enum, auto
from pathlib  import Path
from time     import perf_counter_ns
from typing import Optional as Nullable, Dict, Iterator, Iterable

from ruamel.yaml import YAML, CommentedMap
from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Tree        import Node

from pyEDAA.Reports.OSVVM  import OSVVMException


@export
class AlertLogStatus(Enum):
	Unknown = auto()
	Passed = auto()
	Failed = auto()

	__MAPPINGS__ = {
		"passed": Passed,
		"failed": Failed
	}

	@classmethod
	def Parse(self, name: str) -> "AlertLogStatus":
		try:
			return self.__MAPPINGS__[name.lower()]
		except KeyError as ex:
			raise OSVVMException(f"Unknown AlertLog status '{name}'.") from ex

	def __bool__(self) -> bool:
		return self is self.Passed


def _format(node: Node) -> str:
	return f"{node._value}: {node['TotalErrors']}={node['AlertCountFailures']}/{node['AlertCountErrors']}/{node['AlertCountWarnings']} {node['PassedCount']}/{node['AffirmCount']}"
	# TODO: Python 3.12+
	# return f"{node._value}: {node["TotalErrors"]}={node["AlertCountFailures"]}/{node["AlertCountErrors"]}/{node["AlertCountWarnings"]} {node["PassedCount"]}/{node["AffirmCount"]}"


@export
class AlertLogGroup(metaclass=ExtendedType, slots=True):
	_parent: "AlertLogGroup"
	_name: str
	_children: Dict[str, "AlertLogGroup"]

	_status: AlertLogStatus
	_totalErrors: int
	_alertCountWarnings: int
	_alertCountErrors: int
	_alertCountFailures: int
	_passedCount: int
	_affirmCount: int
	_requirementsPassed: int
	_requirementsGoal: int
	_disabledAlertCountWarnings: int
	_disabledAlertCountErrors: int
	_disabledAlertCountFailures: int

	def __init__(
		self,
		name: str,
		status: AlertLogStatus = AlertLogStatus.Unknown,
		totalErrors: int = 0,
		alertCountWarnings: int = 0,
		alertCountErrors: int = 0,
		alertCountFailures: int = 0,
		passedCount: int = 0,
		affirmCount: int = 0,
		requirementsPassed: int = 0,
		requirementsGoal: int = 0,
		disabledAlertCountWarnings: int = 0,
		disabledAlertCountErrors: int = 0,
		disabledAlertCountFailures: int = 0,
		children: Iterable["AlertLogGroup"] = None,
		parent: Nullable["AlertLogGroup"] = None
	) -> None:
		self._parent = parent
		self._name = name
		self._children = {}
		if children is not None:
			for child in children:
				self._children[child._name] = child
				child._parent = self

		self._status = status
		self._totalErrors = totalErrors
		self._alertCountWarnings = alertCountWarnings
		self._alertCountErrors = alertCountErrors
		self._alertCountFailures = alertCountFailures
		self._passedCount = passedCount
		self._affirmCount = affirmCount
		self._requirementsPassed = requirementsPassed
		self._requirementsGoal = requirementsGoal
		self._disabledAlertCountWarnings = disabledAlertCountWarnings
		self._disabledAlertCountErrors = disabledAlertCountErrors
		self._disabledAlertCountFailures = disabledAlertCountFailures

	@readonly
	def Parent(self) -> Nullable["AlertLogGroup"]:
		return self._parent

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Status(self) -> AlertLogStatus:
		return self._status

	# @readonly
	# def Affirmations(self) -> int:
	# 	return self._afirmations

	@readonly
	def TotalErrors(self) -> int:
		return self._totalErrors

	@readonly
	def AlertCountWarnings(self) -> int:
		return self._alertCountWarnings

	@readonly
	def AlertCountErrors(self) -> int:
		return self._alertCountErrors

	@readonly
	def AlertCountFailures(self) -> int:
		return self._alertCountFailures

	@readonly
	def PassedCount(self) -> int:
		return self._passedCount

	@readonly
	def AffirmCount(self) -> int:
		return self._affirmCount

	@readonly
	def RequirementsPassed(self) -> int:
		return self._requirementsPassed

	@readonly
	def RequirementsGoal(self) -> int:
		return self._requirementsGoal

	@readonly
	def DisabledAlertCountWarnings(self) -> int:
		return self._disabledAlertCountWarnings

	@readonly
	def DisabledAlertCountErrors(self) -> int:
		return self._disabledAlertCountErrors

	@readonly
	def DisabledAlertCountFailures(self) -> int:
		return self._disabledAlertCountFailures

	def __iter__(self) -> Iterator["AlertLogGroup"]:
		return self._chilren.values()

	def __getitem__(self, name: str) -> "AlertLogGroup":
		return self._chilren[name]

	def ToTree(self) -> Node:
		node = Node(
			value=self._name,
			keyValuePairs={
				"TotalErrors": self._totalErrors,
				"AlertCountFailures":  self._alertCountFailures,
				"AlertCountErrors": self._alertCountErrors,
				"AlertCountWarnings": self._alertCountWarnings,
				"PassedCount": self._passedCount,
				"AffirmCount": self._affirmCount
			},
			children=(child.ToTree() for child in self._children.values()),
			format=_format
		)

		return node


@export
class Document(AlertLogGroup):
	_path: Path
	_yamlDocument: Nullable[YAML]

	_analysisDuration: float  #: TODO: replace by Timer; should be timedelta?
	_modelConversion:  float  #: TODO: replace by Timer; should be timedelta?

	def __init__(self, filename: Path, parse: bool = False) -> None:
		super().__init__("", parent=None)
		self._path = filename
		self._yamlDocument = None

		self._analysisDuration = -1.0
		self._modelConversion = -1.0

		if parse:
			self.Read()
			self.Parse()

	@property
	def Path(self) -> Path:
		return self._path

	@readonly
	def AnalysisDuration(self) -> timedelta:
		return timedelta(seconds=self._analysisDuration)

	@readonly
	def ModelConversionDuration(self) -> timedelta:
		return timedelta(seconds=self._modelConversion)

	def Read(self) -> None:
		if not self._path.exists():
			raise OSVVMException(f"OSVVM AlertLog YAML file '{self._path}' does not exist.") \
				from FileNotFoundError(f"File '{self._path}' not found.")

		startAnalysis = perf_counter_ns()
		try:
			yamlReader = YAML()
			self._yamlDocument = yamlReader.load(self._path)
		except Exception as ex:
			raise OSVVMException(f"Couldn't open '{self._path}'.") from ex

		endAnalysis = perf_counter_ns()
		self._analysisDuration = (endAnalysis - startAnalysis) / 1e9

	def Parse(self) -> None:
		if self._yamlDocument is None:
			ex = OSVVMException(f"OSVVM AlertLog YAML file '{self._path}' needs to be read and analyzed by a YAML parser.")
			ex.add_note(f"Call 'Document.Read()' or create document using 'Document(path, parse=True)'.")
			raise ex

		startConversion = perf_counter_ns()

		self._name = self._yamlDocument["Name"]
		self._status = AlertLogStatus.Parse(self._yamlDocument["Status"])
		for child in self._yamlDocument["Children"]:
			alertLogGroup = self._ParseAlertLogGroup(child)
			self._children[alertLogGroup._name] = alertLogGroup
			alertLogGroup._parent = self

		endConversation = perf_counter_ns()
		self._modelConversion = (endConversation - startConversion) / 1e9

	def _ParseAlertLogGroup(self, child: CommentedMap) -> AlertLogGroup:
		results = child["Results"]
		alertLogGroup = AlertLogGroup(
			child["Name"],
			AlertLogStatus.Parse(child["Status"]),
			results["TotalErrors"],
			results["AlertCount"]["Warning"],
			results["AlertCount"]["Error"],
			results["AlertCount"]["Failure"],
			results["PassedCount"],
			results["AffirmCount"],
			results["RequirementsPassed"],
			results["RequirementsGoal"],
			results["DisabledAlertCount"]["Warning"],
			results["DisabledAlertCount"]["Error"],
			results["DisabledAlertCount"]["Failure"],
			children=(self._ParseAlertLogGroup(ch) for ch in child["Children"])
		)

		return alertLogGroup
