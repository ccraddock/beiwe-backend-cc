(function(){
    angular
    .module('surveyBuilder')
    .controller('DataPipelineExecWebFormController', ['$scope', '$window', function($scope, $window) {
        $scope.studyParticipants = studyParticipants;

        console.log('this are the values'+studyParticipants);
    }]);
}());
