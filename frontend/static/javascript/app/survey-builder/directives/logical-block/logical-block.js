angular.module("surveyBuilder")
  .directive("logicalBlock", function(ARITHMETIC_OPERATORS, LOGICAL_OPERATORS, _, logicService) {
    return {
      "link": function(scope) {
        /* Constants */
        scope._ = _;
        scope.ARITHMETIC_OPERATORS = ARITHMETIC_OPERATORS;
        scope.LOGICAL_OPERATORS = LOGICAL_OPERATORS;
        
        scope.$watch("surveyBuilder.currentQuestionFields.question_id", function() {
          scope.type = _.keys(scope.surveyBuilder.getValueAtPath(scope.path))[0];
        });
        scope.getNewPath = function(index) {
          return logicService.getNewPath(scope.path, scope.type, index);
        };
      },
      "restrict": "E",
      "scope": {
        "surveyBuilder": "=",
        "path": "@"
      },
      "templateUrl": "/static/javascript/app/survey-builder/directives/logical-block/logical-block.html"
    };
  });
