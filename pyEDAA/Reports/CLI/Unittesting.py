from argparse import Namespace
from pathlib import Path
from typing import List

from pyTooling.Attributes.ArgParse import CommandHandler
from pyTooling.Attributes.ArgParse.ValuedFlag import LongValuedFlag
from pyTooling.MetaClasses import ExtendedType

from pyEDAA.Reports.Unittesting import MergedTestsuiteSummary
from pyEDAA.Reports.Unittesting.JUnit import JUnitDocument, JUnitReaderMode, UnittestException


class UnittestingHandlers(metaclass=ExtendedType, mixin=True):
	@CommandHandler("merge-unittest", help="Merge unit testing results.", description="Merge unit testing results.")
	@LongValuedFlag("--junit", dest="junit", metaName='JUnitFile', help="Unit testing summary file (XML).")
	def HandleMergeUnittest(self, args: Namespace) -> None:
		"""Handle program calls with command ``merge-unittest``."""
		self._PrintHeadline()

		returnCode = 0
		if args.junit is None:
			print(f"Option '--junit <JUnitFile' is missing.")
			returnCode = 3

		if returnCode != 0:
			exit(returnCode)

		print(f"Merging unit test summary files to a single file ...")

		junitDocuments: List[JUnitDocument] = []
		print(f"  IN (JUnit)  -> Common Data Model:      {args.junit}")
		for file in Path.cwd().glob(args.junit):
			print(f"    reading {file}")
			junitDocuments.append(JUnitDocument(file, parse=True, readerMode=JUnitReaderMode.DecoupleTestsuiteHierarchyAndTestcaseClassName))

		merged = MergedTestsuiteSummary("PlatformTesting")
		for summary in junitDocuments:
			print(f"    merging {summary.Path}")
			merged.Merge(summary)

		print(f"  Common Data Model -> OUT (JUnit):      Unittesting.xml")
		junitDocument = JUnitDocument.FromTestsuiteSummary(Path.cwd() / "Unittesting.xml", merged)
		try:
			junitDocument.Write(regenerate=True, overwrite=True)
		except UnittestException as ex:
			self.WriteError(str(ex))
			if ex.__cause__ is not None:
				self.WriteError(f"  {ex.__cause__}")
