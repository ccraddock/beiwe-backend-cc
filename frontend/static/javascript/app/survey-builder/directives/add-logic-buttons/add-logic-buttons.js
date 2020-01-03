angular.module("surveyBuilder")
  .directive("addLogicButtons", function() {
    return {
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "newPath": "@"
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/add-logic-buttons/add-logic-buttons.html"
    };
  });
