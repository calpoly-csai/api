class Corrections:
    def __init__(
        self,
        correctionId,
        rawText,
        correctionText,
        tableNameToCorrect,
        columnNameToCorrect,
    ):
        self.correction_id = correctionId
        self.raw_text = rawText
        self.correction_text = correctionText
        self.table_name_to_correct = tableNameToCorrect
        self.column_name_to_correct = columnNameToCorrect
        self.is_view = False