(function() {
  
  angular
    .module("surveyBuilder")
    .controller("SurveyBuilderCtrl", SurveyBuilderCtrl);
  
  function SurveyBuilderCtrl($compile, $scope, _, ARITHMETIC_OPERATORS, LOGICAL_OPERATORS, QUESTION_FIELDS_LIST,
                             QUESTION_TYPE_LABELS, QUESTION_TYPES, TEXT_FIELD_TYPES, TEXT_FIELD_TYPE_LABELS, uuid) {
    var vm = this;
    /* Constants for use in template */
    vm.QUESTION_TYPES = QUESTION_TYPES;
    vm.QUESTION_TYPE_LABELS = QUESTION_TYPE_LABELS;
    vm.TEXT_FIELD_TYPES = TEXT_FIELD_TYPES;
    vm.TEXT_FIELD_TYPE_LABELS = TEXT_FIELD_TYPE_LABELS;
    vm.QUESTION_FIELDS_LIST = QUESTION_FIELDS_LIST;
    vm.LOGICAL_OPERATORS = LOGICAL_OPERATORS;
    vm.ARITHMETIC_OPERATORS = ARITHMETIC_OPERATORS;
    vm.errors = null;
    vm.formatErrors = function(errors) {
      /**
       * Formats errors returned from validating survey
       */
      var formattedErrors = [];
      if (errors === null) {
        return formattedErrors;
      }
      _.forEach(errors, function(value, key) {
        if (key == "duplicate_uuids") {
          if (value.length > 0) {
            // There are duplicate uuids - almost impossible to happen, but could
            formattedErrors.push("There are duplicate UUIDs - please refresh the page and try again.");
          }
        } else {
          var questionNumber = _.indexOf(vm.questionIds, key) + 1;
          formattedErrors.push("Question " + questionNumber + ": " + value[0]);
        }
      });
      return formattedErrors;
    };

    /* Variables from django template */
    vm.questions = window.questions;
    vm.randomize = window.randomize;
    vm.randomizeWithMemory = window.randomizeWithMemory;
    vm.numberOfRandomQuestions = window.numberOfRandomQuestions;
    // vm.questionIds is set below in vm.refreshQuestionIds()

    /* Current question for displaying/modifying with modal */
    vm.currentQuestionFields = {
      "question_text": "",
      "question_type": QUESTION_TYPES.infoTextBox,
      "min": "",
      "max": "",
      "text_field_type": TEXT_FIELD_TYPES.numeric,
      "is_new_question": true,
      "index": null,
      "question_id": null,
      "answers": [],
      "display_if": null
    };
    vm.defaultQuestionFields = angular.copy(vm.currentQuestionFields);

    /**
     * Edit question modal actions
     */
    vm.addNewQuestion = function() {
      /**
       * Adds a new question based on information from vm.currentQuestionFields
       */
      var questionObject = vm.getCurrentQuestionObject();
      // Generate a new UUID since this is a new question
      questionObject["question_id"] = uuid.generate();
      vm.questions.push(questionObject);
      vm.refreshQuestionIds();
    };

    vm.editQuestion = function() {
      /**
       * Edits the question in vm.questions based on information in vm.currentQuestionFields\
       */
      var questionObject = vm.getCurrentQuestionObject();
      vm.questions.splice(vm.currentQuestionFields.index, 1, questionObject);
    };
    
    vm.addAnswerField = function() {
      /**
       * Adds a field to vm.currentQuestionFields.answers array
       */
      vm.currentQuestionFields.answers.push({"text": ""});
    };

    vm.deleteAnswerField = function(index) {
      /**
       * Removes the field in vm.currentQuestionFields.answers array at the passed index
       */
      vm.currentQuestionFields.answers.splice(index, 1);
    };


    /**
     * Edit question modal helper functions
     */
    vm.resetQuestionModal = function(overrides) {
      /**
       * Resets the edit question modal to its default, overwriting the default with anything passed to overrides
       *
       * Args:
       *   overrides (object): the question object to overwrite with
       */
      $("edit-question").remove();
      vm.currentQuestionFields = angular.copy(vm.defaultQuestionFields);
      _.extend(vm.currentQuestionFields, overrides);
      $("body").append($compile('<edit-question survey-builder="surveyBuilder" show="true"></edit-question>')($scope));
    };

    vm.populateEditQuestionModal = function(index) {
      /**
       * Populates the edit question modal with information from the question in vm.questions at the passed index
       */
      vm.resetQuestionModal(vm.questions[index]);
      vm.currentQuestionFields.is_new_question = false;
      vm.currentQuestionFields.index = index;
      /* If the min and max values are strings, turn them into ints */
      vm.currentQuestionFields.min = parseInt(vm.currentQuestionFields.min);
      vm.currentQuestionFields.max = parseInt(vm.currentQuestionFields.max);
    };

    vm.getCurrentQuestionObject = function() {
      /**
       * Returns an object with the correct fields for sending to the backend from data in vm.currentQuestionFields
       */
      var currentQuestionObject = _.pick(vm.currentQuestionFields, QUESTION_FIELDS_LIST[vm.currentQuestionFields.question_type]);
      return currentQuestionObject;
    };

    vm.checkSliderValue = function(min_or_max) {
      /**
       * Checks if a slider value (min or max) is within the allowed range. If not, sets it to the minimum
       * or maximum depending on which side it is out of range on.
       */
      var input = $("#" + min_or_max);
      var currentValue = parseInt(input.val(), 10);
      var minimumValue = parseInt(input.attr("min"), 10);
      var maximumValue = parseInt(input.attr("max"), 10);
      if (currentValue < minimumValue) {
        vm.currentQuestionFields[min_or_max] = minimumValue;
      } else if (currentValue > maximumValue) {
        vm.currentQuestionFields[min_or_max] = maximumValue;
      }
    };

    /**
     * Question summary actions
     */
    vm.moveQuestionUp = function(index) {
      /**
       * Move the question at the passed index up in order in vm.questions
       */
      if (index > 0 && index <= vm.questions.length-1) {
        vm.questions.splice(index - 1, 2, vm.questions[index], vm.questions[index - 1]);
        vm.refreshQuestionIds();
      }
    };

    vm.moveQuestionDown = function(index) {
      /**
       * Move the question at the passed index down in order in vm.questions
       */
      if (index >= 0 && index < vm.questions.length-1) {
        vm.questions.splice(index, 2, vm.questions[index + 1], vm.questions[index]);
        vm.refreshQuestionIds();
      }
    };

    vm.deleteQuestion = function(index) {
      /**
       * Delete the question at the passed index in vm.questions
       */
      vm.questions.splice(index, 1);
      vm.refreshQuestionIds();
    };

    /**
     * Skip logic actions
     */
    vm.addOrBlock = function(path) {
      /**
       * Adds an OR block to the display_if nested object at the path specified
       */
      vm.addValueToPath(path, {"or": []})
    };
    
    vm.addAndBlock = function(path) {
      /**
       * Adds an OR block to the display_if nested object at the path specified
       */
      vm.addValueToPath(path, {"and": []})
    };

    vm.addConditionalBlock = function(path) {
      /**
       * Adds a conditional block to the display_if nested object at the path specified
       */
      vm.addValueToPath(path, {"==": [vm.questionIds[0], ""]})
    };

    vm.addNotBlock = function(path) {
      /**
       * Adds a NOT block to the display_if nested object at the path specified
       */
      vm.addValueToPath(path, {"not": {}})
    };

    vm.deleteBlock = function(path) {
      /**
       * Deletes the logical or conditional block at the path specified
       */
      var pathLocationArray = vm.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      if (_.isArray(parentObject)) {
        parentObject.splice(key, 1);
      } else {
        // This case should only be true for the base AND or OR block
        parentObject[key] = null;
      }
    };
    

    /**
     * Skip logic helper functions
     */
    vm.getPathLocation = function(path) {
      /**
       * Navigates to the passed in path from vm.currentQuestionFields.display_if and returns and array with
       * the parent location and last key. For example, if the path is "or/3", the referenced location is
       * vm.currentQuestionFields.display_if["or"]["3"], and this function will return
       * [vm.currentQuestionFields.display_if["or"], "3"].
       *
       * Args:
       *   path (string): the path to navigate to
       * Returns:
       *   (array): [parentLocation (object/array), lastKey (string)]
       */
      var pathKeys = ["display_if"].concat(path.match(/[^\/]+/g) || []);
      var lastKey = pathKeys.pop();
      var currentLocation = vm.currentQuestionFields;
      _.forEach(pathKeys, function(key) {
        if (typeof currentLocation === "undefined") {
          alert("Sorry, something went wrong with adding this field (" + path + ").");
          return false;
        }
        currentLocation = currentLocation[key]
      });
      return [currentLocation, lastKey]
    };
    
    vm.getValueAtPath = function(path) {
      /**
       * Returns the value at the path given.
       */
      var pathLocationArray = vm.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      return parentObject[key];
    };
    
    vm.addValueToPath = function(path, value) {
      /**
       * Adds the passed value to the path from root vm.currentQuestionFields.display_if. The path should be a string
       * that's delimited with "/" for each level).
       */
      var pathLocationArray = vm.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      if (_.isArray(parentObject[key])) {
        parentObject[key].push(value);
      } else {
        parentObject[key] = value;
      }
    };
    
    vm.updateOperatorAtPath = function(path, element) {
      /**
       * Updates the operator at the path specified (this is because editing an object attribute is non-trivial
       * compared to editing a value).
       * 
       * Args:
       *   path (string): path to edit
       *   element (element): logic or conditional block element used to retrieve the operator type from its scope
       */
      var pathLocationArray = vm.getPathLocation(path);
      var parentObject = pathLocationArray[0];
      var key = pathLocationArray[1];
      var currentOperator = vm.getOperatorType(parentObject[key]);
      var updatedOperator = element.type;
      var updatedStatement = {};
      updatedStatement[updatedOperator] = parentObject[key][currentOperator];
      if (_.isArray(parentObject)) {
        // This operator is within an array, so we splice it in
        parentObject.splice(key, 1, updatedStatement);
      } else {
        // This operator is within an object, so we replace the whole object
        parentObject[key] = updatedStatement;
      }
    };
    
    vm.getOperatorType = function(value) {
      /**
       * Returns the type of operation at this level in the skip logics ("AND", "OR", "==", "<", etc.)
       */
      return _.keys(value)[0];
    };
    
    vm.getQuestionIds = function() {
      /**
       * Returns an array of question_ids from vm.questions
       */
      return _.map(vm.questions, "question_id");
    };
    
    vm.refreshQuestionIds = function() {
      /**
       * Refreshes vm.questionIds
       */
      vm.questionIds = vm.getQuestionIds();
    };
    // Set vm.questionIds
    vm.refreshQuestionIds();
    
  }

})();