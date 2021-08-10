import datetime
from dataclasses import dataclass
from typing import List

from cutlistgenerator.error import ProductNotInKitException
from cutlistgenerator.database.cutlistdatabase import CutListDatabase