angular.module("surveyBuilder")
  .service("uuid", function() {
    this.generate = function() {
      var d = new Date().getTime();
      return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == "x" ? r : (r & 0x7 | 0x8)).toString(16);
      });
    }
  })
  .factory("logicService", function() {
    return {
      getNewPath: getNewPath
    };
    
    ////////
    
    function getNewPath(path, type, index) {
      var newPath = path + "/" + type;
      if (typeof index != "undefined") {
        newPath = newPath + "/" + index;
      }
      return newPath;
    }
  });
