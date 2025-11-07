from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import orjson
import time


@dataclass
class RecorderConfig:
	root: Path
	atomic: bool = True


class DataRecorder:
	def __init__(self, config: RecorderConfig) -> None:
		self.root = config.root
		self.atomic = config.atomic
		(self.root / "data" / "raw").mkdir(parents=True, exist_ok=True)
		(self.root / "data" / "processed").mkdir(parents=True, exist_ok=True)
		(self.root / "analysis" / "validation").mkdir(parents=True, exist_ok=True)
		(self.root / "visualizations" / "static").mkdir(parents=True, exist_ok=True)
		(self.root / "visualizations" / "interactive").mkdir(parents=True, exist_ok=True)

	def _run_file(self, run_id: int) -> Path:
		return self.root / "data" / "raw" / f"run_{run_id:04d}.json"

	def start_run(self, run_id: int) -> None:
		fpath = self._run_file(run_id)
		with open(fpath, "wb") as f:
			f.write(b"[")

	def append_step(self, run_id: int, record: Dict[str, Any], is_last: bool = False) -> None:
		fpath = self._run_file(run_id)
		with open(fpath, "ab") as f:
			data = orjson.dumps(record)
			f.write(data)
			if not is_last:
				f.write(b",\n")

	def end_run(self, run_id: int) -> None:
		fpath = self._run_file(run_id)
		with open(fpath, "ab") as f:
			f.write(b"]\n")

	def write_validation_report(self, name: str, content: str) -> Path:
		path = self.root / "analysis" / "validation" / name
		path.write_text(content, encoding="utf-8")
		return path

	def write_processed(self, filename: str, data_bytes: bytes) -> Path:
		path = self.root / "data" / "processed" / filename
		path.write_bytes(data_bytes)
		return path
