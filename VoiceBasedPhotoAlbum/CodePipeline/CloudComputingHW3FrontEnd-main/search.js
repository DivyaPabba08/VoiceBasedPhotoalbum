function searchPhoto() {

  var apigClient = apigClientFactory.newClient({
    apiKey: 'R25b90jDOY7a05Ug9c3I563sr9k9kE7763ufHTAn'
  });

  var image_message = document.getElementById("note-textarea").value;
  if(image_message == "")
    var image_message = document.getElementById("transcript").value;
  console.log(image_message);

  var body = {};
  var params = {
    q: image_message,
    'x-api-key': 'R25b90jDOY7a05Ug9c3I563sr9k9kE7763ufHTAn'
  };
  var additionalParams = {
    headers: {
      'Content-Type': "application/json",
    },
  };

  apigClient.searchGet(params, body, additionalParams)
    .then(function (result) {
      response_data = result.data;
      document.getElementById("img-container").innerHTML = "";
      var para = document.createElement("p");
      para.setAttribute("id", "displaytext");
      document.getElementById("img-container").appendChild(para); 
      console.log(response_data);
      console.log(response_data.length);
      if (response_data.length == 0) {
        document.getElementById("displaytext").innerHTML = "No Images Found !!!";
        document.getElementById("displaytext").style.display = "block";
      }
      response_data.forEach(function (obj) {
        var img = new Image();
        img.src = obj;
        img.setAttribute("class", "banner-img");
        img.setAttribute("alt", "effy");
        img.setAttribute("width", "150");
        img.setAttribute("height", "100");
        document.getElementById("displaytext").innerHTML = "Images returned are : ";
        document.getElementById("img-container").appendChild(img);
        document.getElementById("displaytext").style.display = "block";

      });
    }).catch(function (result) {
    });

}
