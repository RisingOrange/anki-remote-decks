from aqt import mw

from .. import config


class AnkiNoteBuilder:

    def __init__(self, defaultDeck=config.defaultDeck):
        self.defaultDeck = defaultDeck
        self.oldDefaultDeck = defaultDeck

    def built_note(self, anki_note):

        # Check if should use no base deck
        if anki_note.getParameter("baseDeck", "true").lower() == "true":
            self.defaultDeck = self.oldDefaultDeck
        else:
            self.defaultDeck = None

        # All decks stored under default deck
        if anki_note.deckName == "" or anki_note.deckName is None:
            # TODO log note was built on default deck
            deckName = self.defaultDeck
        deckName = self._getFullDeckPath(anki_note.deckName)

        # Defaults to basic type by default
        modelName = anki_note.getParameter("Note type", "Basic")

        note = {"deckName": deckName, "modelName": modelName}
        note["tags"] = anki_note.getTags()

        note["fields"] = dict()
        field_infos = mw.col.models.by_name(modelName)['flds']
        field_names = [field["name"] for field in field_infos]

        note["fields"][field_names[0]] = self.createQuestionString(anki_note.getAllParamters(), anki_note.getQuestions())
        answers = anki_note.getAnswers()
        for field_name, answer in zip(field_names[1:], answers):
            note["fields"][field_name] = answer

        return note

    def createQuestionString(self, ankiParamters, questions):

        if len(questions) == 1:
            question = questions[0].replace("\n", "<br>")
            return question
        else:
            questionString = ""
            for q in questions:
                q = self._formatString(q)
                q = q.strip().replace("\n", "<br>")
                questionString += q + " <br>"
            return questionString

    def createAnswerString(self, ankiParamters, answers):

        answerString = ""

        # Check for list type
        listType = ankiParamters.get("list", "unordered").lower()

        if listType == "false" or listType == "none":
            for i in answers:
                i = self._formatString(i)
                if isinstance(i, str):
                    answerString += i + "<br>"  # HTML link break
                elif isinstance(i, list):
                    answerString += self.createAnswerString(ankiParamters, i)
            return answerString

        listTag = "ul"  # Default option

        if listType == "unordered" or listType == "ul":
            listTag = "ul"
        elif listType == "ordered" or listType == "ol":
            listTag = "ol"

        # Only create list if answers exits
        if len(answers) > 0:
            # Can only can create single level of indentation. Align bulletpoints
            answerString += "<{} style='list-style-position: inside;'>".format(
                listTag)
            for i in answers:
                i = self._formatString(i)
                if isinstance(i, str):
                    answerString += "<li>" + i + "</li>"
                elif isinstance(i, list):
                    answerString += self.createAnswerString(ankiParamters, i)
                else:
                    raise Exception(
                        "Unsupported action with answer string from => " + str(i))

            answerString += "</{}>".format(listTag)

        return answerString

    def _getFullDeckPath(self, deckName):  # (str)
        if self.defaultDeck == None:
            return str(deckName)
        else:
            return str(self.defaultDeck + "::" + deckName)

    def _formatString(self, unformattedString):

        return unformattedString
