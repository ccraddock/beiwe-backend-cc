angular.module("surveyBuilder")
  .constant("QUESTION_TYPES", {
    "infoTextBox": "info_text_box",
    "slider": "slider",
    "radio": "radio_button",
    "checkbox": "checkbox",
    "freeResponse": "free_response"
  })
  // We use .service() here instead of .constant() since you can't inject into .constant(). Behavior emulates the same
  // behavior as a .constant(); http://stackoverflow.com/a/23544466
  .service("QUESTION_TYPE_LABELS", function(QUESTION_TYPES) {
    this[QUESTION_TYPES.infoTextBox] = "Informational Text";
    this[QUESTION_TYPES.slider] = "Slider";
    this[QUESTION_TYPES.radio] = "Radio Button";
    this[QUESTION_TYPES.checkbox] = "Checkbox";
    this[QUESTION_TYPES.freeResponse] = "Free Response";
  })
  .service("QUESTION_FIELDS_LIST", function(QUESTION_TYPES) {
    /**
     * A list of the keys necessary for each question type
     */
    var commonKeys = ["question_id", "question_text", "question_type", "display_if"];
    this[QUESTION_TYPES.infoTextBox] = commonKeys;
    this[QUESTION_TYPES.slider] = commonKeys.concat(["max", "min"]);
    this[QUESTION_TYPES.radio] = commonKeys.concat(["answers"]);
    this[QUESTION_TYPES.checkbox] = commonKeys.concat(["answers"]);
    this[QUESTION_TYPES.freeResponse] = commonKeys.concat(["text_field_type"]);
  })
  .constant("TEXT_FIELD_TYPES", {
    "numeric": "NUMERIC",
    "singleLine": "SINGLE_LINE_TEXT",
    "multiLine": "MULTI_LINE_TEXT"
  })
  .service("TEXT_FIELD_TYPE_LABELS", function(TEXT_FIELD_TYPES) {
    this[TEXT_FIELD_TYPES.numeric] = "Numeric";
    this[TEXT_FIELD_TYPES.singleLine] = "Single-line Text";
    this[TEXT_FIELD_TYPES.multiLine] = "Multi-line Text";
  })
  .constant("LOGICAL_OPERATORS", ["and", "or", "not"])
  .constant("ARITHMETIC_OPERATORS", ["==", "<", "<=", ">", ">="]);