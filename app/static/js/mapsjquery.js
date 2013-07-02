

var map;
var last_infowindow = new google.maps.InfoWindow();
//var infowindow = new google.maps.InfoWindow();
var loading, fail_whale

// Following bootbox.js example
//
$("#myModal").on("show", function() {    // wire up the OK button to dismiss the modal when shown
        $("#myModal a.btn").on("click", function(e) {
            console.log("button pressed");   // just as an example...
            $("#myModal").modal('hide');     // dismiss the dialog
        });
    });
 
    $("#myModal").on("hide", function() {    // remove the event listeners when the dialog is dismissed
        $("#myModal a.btn").off("click");
    });
    
    $("#myModal").on("hidden", function() {  // remove the actual elements from the DOM when fully hidden
        $("#myModal").remove();
    });
    
    $("#myModal").modal({                    // wire up the actual modal functionality and show the dialog
      "backdrop"  : "static",
      "keyboard"  : true,
      "show"      : true                     // ensure the modal is shown immediately
    });

$(document).ready(function() {
    $('#myModal').modal()

    // put all your jQuery goodness in here.
});

window.onload = function () {
                //alert('big test!!!!')
                //bootstrap_alert.warning('big test');
                // loading = document.createElement("img");
                // loading.id = 'loading'
                // loading.src = "/static/images/twitter_fail_whale.png";
                // loading.setAttribute('width', '10%');
                // loading.setAttribute('height','10%');
                loading = document.createElement("div");
                //loading.innerHTML='<img src="/static/images/loading.gif" class="img-rounded" style="height: 50; width: 50" id="loading-indicator"/>';
                loading.innerHTML='<div class="row-fluid"> \
                  <div class="span12 pagination-centered"><img src="/static/images/ajax-loader.gif" style="height: 60; width: 60" /></div></div>'
                fail_whale = document.createElement("div");
                fail_whale.innerHTML='<div class="row-fluid"> \
                      <blockquote><p> \
                      Twitter is over capacity </p><small>Please wait a few minutes and try again.</small> \
                      </blockquote> \
                  <div class="span12 pagination-centered"><img src="/static/images/twitter_fail_whale.png" style="height: 170; width: 270" /></div></div>';
                
                //<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            }

function initialize() {
  var mapOptions = {
    zoom: 4,
    center: new google.maps.LatLng(41.03,28.92),
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  map = new google.maps.Map(document.getElementById('map-canvas'),
      mapOptions);
  google.maps.event.addListener(map, 'click', function(event){
    console.log('Lat: ' + event.latLng.lat() + ' and Longitude is: ' + event.latLng.lng());
    placeMarker('/get_tweet', event.latLng);
  });
}

function placeMarker(api,location) {
  var marker = new google.maps.Marker({
    position: location,
    map: map
  });

  //content="<div font='serif' style='color:#4099FF>Loading tweets...</div> "

  // var caption="<div style='max-height:200px; overflow-y:auto'>";
  // //caption=caption+'<span class="label label-success">Loading...</span>';
  // caption=caption+'<div class="page-header"> \
  //     <h2>Loading...</h2> \
  //     </div>';
  // caption=caption+'</div>';
  //var caption = '<img src="/images/twitter_fail_whale.png" id="loading-indicator"/>';
  var caption = 'loading'

  var infowindow = new google.maps.InfoWindow({
    content: loading,
    maxWidth: 500
  });
  // var DOM_img = document.createElement("img");
  // DOM_img.id = 'fail_whale'
  // DOM_img.src = "/static/images/twitter_fail_whale.png";
  //var map_children = map.childNodes;
  //console.log(map_children);
  //map.infowindow.appendChild(DOM_img);
  
  //infowindow.setContent(document.getElementById('fail_whale'));
  last_infowindow.close();
  infowindow.open(map,marker);
  last_infowindow=infowindow;

  google.maps.event.addListener(marker, 'click', function() {
    last_infowindow.close();
    infowindow.close();
    //infowindow.setContent(document.getElementById('fail_whale'));
    infowindow.open(map,marker);
    last_infowindow=infowindow;
    console.log('just switched windows...')
  });

  var lat = location.lat()
  var lon = location.lng()

  //var data = {'location': 'foofoo'}
  //console.log(data)

  function callback(data) {
    //console.log(data)
    var news_type;
    // var content = '<blockquote class="twitter-tweet"><a href="https://twitter.com/twitterapi/status/347489674153033729"></a></blockquote>'
    // content=content+'<script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'
    
    // Create a regular expression for
    // extracting links
    var http_regex = /(http:\/\/[a-zA-Z0-9_\.\-\+\&\!\#\~\/\,]+)/g;
    var chopped = /(http:\/\/[a-zA-Z0-9_\.\-\+\&\!\#\~\/\,]+)\u2026$/;

    function replacer(url) {
      return '<a href="'+url+'" target="_blank" >'+url+'</a>';
    };
    console.log(data.result.errors);
    if (data.result.errors===1) {
      caption="<blockquote><p>No tweets are currently available from this location.  Please click somewhere else! </p></blockquote> ";
    }
    else if (data.result.errors===2) {
      //var caption="<div font='calibri' style='color:#4099FF'>The Twitter API is under heavy load. \n Please try again later.</div> ";
      caption=fail_whale;
    }
    else {
      var caption="<div style='max-height:200px; overflow-y:auto'>";
      caption=caption+'<span class="label label-success">Top News Tweets</span>';
      for (var i=0;i<data.result.news_tweets.length;i++) {
        tweet=data.result.news_tweets[i];
        user_name=data.result.news_tweets_names[i];
        prob=data.result.news_tweets_prob[i];
        if (!chopped.test(tweet)) {
          tweet=tweet.replace(http_regex,replacer);
        }
        console.log(tweet)
        caption=caption+"<blockquote> <p>";
        caption=caption+tweet;
        caption=caption+"</p> <small>@"+user_name+"</small></blockquote>";
      };

      caption=caption+'<span class="label label-warning">Other Popular Tweets</span>';
      for (var i=0;i<data.result.other_tweets.length;i++) {
        tweet=data.result.other_tweets[i];
        prob=data.result.other_tweets_prob[i];
        user_name=data.result.other_tweets_names[i];
        if (!chopped.test(tweet)) {
          tweet=tweet.replace(http_regex,replacer);
        }
        console.log(tweet)
        caption=caption+"<blockquote> <p>";
        caption=caption+tweet;
        caption=caption+"</p> <small>@"+user_name+"</small></blockquote>";
      };
      caption=caption+"</div>"
      caption=caption+'<p class="text-center"><span class="badge">Scroll to see more tweets</span></p>'

      // // The code below is good example code and it works!!!
      // var caption="<div style='max-height:200px; overflow-y:auto'>"
      // caption=caption+'<span class="label label-success">Top News Stories</span>'
      // // daption=caption+'<div class="alert"> \
      // //     <strong>Warning!</strong> Best check yo self \
      // //     </div>';
      // caption=caption+'<blockquote> \
      //     Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer \
      //     posuere erat a <a href="http://www.google.com">google</a> foo foo foo </blockquote>'
      // caption=caption+'</div>'
    }
    //console.log(caption)
    infowindow.setContent(caption);
    last_infowindow.close();
    infowindow.open(map,marker);
    last_infowindow=infowindow;
  }

  /*$.ajax({
    url: api,
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json; charset=utf-8',
    mimeType: 'string',
    data: JSON.stringify(data)
  })
    .done(callback);*/
  $.ajax({
    url: api,
    type: 'POST',
    dataType: 'json',
    data: {'lat': lat, 'lon': lon},
    success: callback});

  //url='/_add_numbers'
  //data={a: 94,b:110}


  //$.getJSON(url, {'a': 94, 'b': 110}, callback);

  /*$.ajax({
  dataType: "json",
  type: 'POST',
  url: url,
  data: {'a': 94, 'b':110},
  success: callback});*/

  //$.get('/get_tweet',{'foo': 9}, function (data) {log.console(data);},'json');

  /*$.post('/get_tweet', function(data) {
  alert('Load was performed.');*/

  
  //map.setCenter(location);
};

/**
 * Start the page
 */

$(document).ready(function() {

  //create the map
  google.maps.event.addDomListener(window, 'load', initialize);
});


