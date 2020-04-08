from QA import db
from Entity.ProfessorSectionView import ProfessorSectionView

print(db._get_property_from_entity(
    "section_name",
    ProfessorSectionView,
    "Irene Humer"
))