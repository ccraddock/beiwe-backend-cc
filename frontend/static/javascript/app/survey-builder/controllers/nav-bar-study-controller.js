(function(){
    angular
    .module('surveyBuilder')
    .controller('NavBarStudyController', ['$scope', '$window', function($scope, $window) {
        $scope.navBarStudies = $window.navBarStudies;
    }]);
}());
