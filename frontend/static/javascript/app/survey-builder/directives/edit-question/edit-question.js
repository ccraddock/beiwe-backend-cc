angular.module("surveyBuilder")
  .directive("editQuestion", function() {
    return {
      link: link(),
      restrict: "E",
      scope: {
        show: "@?",
        surveyBuilder: "="
      },
      templateUrl: "/static/javascript/app/survey-builder/directives/edit-question/edit-question.html"
    };
    
    ////////
    
    function link() {
      return function(scope) {
        if (scope.show) {
          // Default to showing the modal
          $('#editQuestionModal').modal("show");
        }
      }
    }
  });
