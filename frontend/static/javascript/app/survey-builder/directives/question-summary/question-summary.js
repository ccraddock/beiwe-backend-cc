angular.module("surveyBuilder")
  .directive("questionSummary", function() {
    return {
      "restrict": "E",
      "templateUrl": "/static/javascript/app/survey-builder/directives/question-summary/question-summary.html"
    };
  });
