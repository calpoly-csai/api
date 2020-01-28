class Courses:

    def __init__(self, courseId, dept, courseNum, termsOffered, units,
                 courseName, raw_concurrent_text, raw_recommended_text,
                 raw_prerequisites_text, crossListedAs, raw_standing_text,
                 standing):
        self.courseId = courseId
        self.dept = dept
        self.courseNum = courseNum
        self.termsOffered = termsOffered
        self.units = units
        self.courseName = courseName
        self.raw_concurrent_text = raw_concurrent_text
        self.raw_recommended_text = raw_recommended_text
        self.raw_prerequisites_text = raw_prerequisites_text
        self.crossListedAs = crossListedAs
        self.raw_standing_text = raw_standing_text
        self.standing = standing
