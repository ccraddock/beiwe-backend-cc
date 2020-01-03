(function(){
    angular
    .module('surveyBuilder')
    .controller('DataAccessWebFormController', ['$scope', '$window', function($scope, $window) {
        $scope.allowedStudies = allowedStudies;
        $scope.participantsByStudy = participantsByStudy;
    }]);
}());
