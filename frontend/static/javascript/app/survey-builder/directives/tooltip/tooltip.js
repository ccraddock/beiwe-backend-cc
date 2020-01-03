angular.module("surveyBuilder")
  .directive("tooltip", function() {
    return {
      "restrict": "A",
      "link": function(scope, element, attributes) {
        $(element).tooltip();
      }
    };
  });
