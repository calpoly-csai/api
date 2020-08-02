#!/usr/bin/env python3
"""
This module holds the expected keys for each Entity type.
"""

from Entity.AudioSampleMetaData import AudioSampleMetaData, NoiseLevel
from Entity.Calendars import Calendars
from Entity.Clubs import Clubs
from Entity.Courses import Courses
from Entity.ErrorLog import ErrorLog
from Entity.Locations import Locations
from Entity.QueryFeedback import QueryFeedback
from Entity.QuestionAnswerPair import QuestionAnswerPair, AnswerType
from Entity.QuestionLog import QuestionLog
from Entity.OfficeHours import OfficeHours
from Entity.Professors import ProfessorsProperties
from Entity.Profs import Profs
from Entity.Professors import Professors
from Entity.ProfessorSectionView import ProfessorSectionView
from Entity.Sections import Sections, SectionType

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
