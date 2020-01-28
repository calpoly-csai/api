class Corrections:

    def __init__(self, correctionId, rawText, correctionText,
                 tableNameToCorrect, columnNameToCorrect):
        self.correctionId = correctionId
        self.rawText = rawText
        self.correctionText = correctionText
        self.tableNameToCorrect = tableNameToCorrect
        self.columnNameToCorrect = columnNameToCorrect
