(function(){
    angular
    .module('surveyBuilder')
    .controller('DataPipelineWebFormController', ['$scope', '$window', function($scope, $window) {
        $scope.downloadableStudies = downloadableStudies;
        $scope.tagsByStudy = tagsByStudy;
    }]);
}());
