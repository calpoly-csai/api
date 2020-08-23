#!/usr/bin/env python3
"""
This module holds the expected keys for each Entity type.
"""

from .AudioSampleMetaData import AudioSampleMetaData, NoiseLevel
from .Calendars import Calendars
from .Clubs import Clubs
from .Courses import Courses
from .ErrorLog import ErrorLog
from .Locations import Locations
from .QueryFeedback import QueryFeedback
from .QuestionAnswerPair import QuestionAnswerPair, AnswerType
from .QuestionLog import QuestionLog
from .OfficeHours import OfficeHours
from .Professors import ProfessorsProperties
from .Profs import Profs
from .Professors import Professors
from .ProfessorSectionView import ProfessorSectionView
from .Sections import Sections, SectionType

# Supported Entities only and their expected keys
EXPECTED_KEYS_BY_ENTITY = {
    AudioSampleMetaData: [
        "is_wake_word",
        "first_name",
        "last_name",
        "gender",
        "noise_level",
        "location",
        "tone",
        "timestamp",
        "username",
        "audio_file_id",
        "script",
        "emphasis"
    ],
    Clubs: [
        "club_name",
        "types",
        "desc",
        "contact_email",
        "contact_email_2",
        "contact_person",
        "contact_phone",
        "box",
        "advisor",
        "affiliation",
    ],
    Calendars: [
        'date',
        'day',
        'month',
        'year',
        'raw_events_text',
    ],
    Courses: [
        'dept',
        'course_num',
        'course_name',
        'units',
        'prerequisites',
        'corequisites',
        'concurrent',
        'recommended',
        'terms_offered',
        'ge_areas',
        'desc',
    ],
    ErrorLog: [
        "question",
        "stacktrace",
        "timestamp",
    ],
    Locations: [
        "building_number",
        "name",
        "longitude",
        "latitude",
    ],
    Sections: [
        "section_name",
        "instructor",
        "alias",
        "title",
        "phone",
        "office",
        "type",
        "days",
        "start",
        "end",
        "location",
        "department",
    ],
    QuestionAnswerPair: [
        "can_we_answer",
        "verified",
        "answer_type",
        "question_format",
        "answer_format",
    ],
    QueryFeedback: [
        "question",
        "answer",
        "answer_type",
        "timestamp",
    ],
    QuestionLog: [
        "question",
        "timestamp",
    ],
    Professors: [
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "research_interests",
        "office",
    ]
}
