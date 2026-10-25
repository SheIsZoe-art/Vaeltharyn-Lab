"""Paths and shared semantics of the laboratory schema."""
from pathlib import Path
import gzip,json
LAB=Path(__file__).resolve().parents[1];REPO=LAB.parent
SCHEMA=2
RELATIONS={'same_sense','source_broader','source_narrower','uncertain','rejected'}
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def jsonlines(path):
 with gzip.open(path,'rt',encoding='utf-8') as stream:
  for line in stream:yield json.loads(line)
def proposals():return read(LAB/'proposals/batch-001.json')
def assessments():return read(LAB/'mappings/assessments.json')
def cases():return assessments()+proposals()
