

var map;
var last_infowindow = new google.maps.InfoWindow();

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

  var infowindow = new google.maps.InfoWindow({
    content: "<div font='calibri' style='color:#4099FF'>Loading tweets...This may take a few seconds.</div>",
    maxWidth: 500
  });
  infowindow.open(map,marker);

  google.maps.event.addListener(marker, 'click', function() {
    last_infowindow.close();
    infowindow.open(map,marker);
    last_infowindow=infowindow;
    console.log('just switched windows...')
  });

  var lat = location.lat()
  var lon = location.lng()

  //var data = {'location': 'foofoo'}
  //console.log(data)

  function callback(data) {
    console.log(data)
    var news_type;
    // var content = '<blockquote class="twitter-tweet"><a href="https://twitter.com/twitterapi/status/347489674153033729"></a></blockquote>'
    // content=content+'<script src="//platform.twitter.com/widgets.js" charset="utf-8"></script>'
    
    // Create a regular expression for
    // extracting links
    var http_regex = /(http:\/\/[a-zA-Z0-9_\.\-\+\&\!\#\~\/\,]+)/;
    var chopped = /(http:\/\/[a-zA-Z0-9_\.\-\+\&\!\#\~\/\,]+)\u2026$/;

    function replacer(url) {
      return "<a font='calibri' style='color:#4099FF' href="+url+' >'+url+'</a>';
    };
    if (data.result.errors===2) {
      var caption="<div font='calibri' style='color:#4099FF'>No tweets are currently available from this location.  Please click somewhere else! \n Please try again later.</div> ";
    }
    if (data.result.errors===2) {
      var caption="<div font='calibri' style='color:#4099FF'>The Twitter API is under heavy load. \n Please try again later.</div> ";
    }
    // else {
    //   var caption="<div font='calibri' style='color:#4099FF'>Most Popular News Tweets:</div> ";
    //   var tweet="<p font='calibri'>"
    //   for (var i=0;i<data.result.news_tweets.length;i++) {
    //     tweet=data.result.news_tweets[i];
    //     prob=data.result.news_tweets_prob[i];
    //     if (!chopped.test(tweet)) {
    //       tweet=tweet.replace(http_regex,replacer);
    //     }
    //     caption=caption+"</p> <p font='calibri'> "+tweet;
    //   };
    //   caption=caption+"</p>"

    //   caption=caption+"<div style='color:#4099FF'>Other Popular Tweets:</div> <p font='calibri'>";
    //   for (var i=0;i<data.result.other_tweets.length;i++) {
    //     tweet=data.result.other_tweets[i];
    //     prob=data.result.other_tweets_prob[i];
    //     if (!chopped.test(tweet)) {
    //       tweet=tweet.replace(http_regex,replacer);
    //     }
    //     caption=caption+"</p> <p font='calibri'> "+tweet;
    //   };
    //   caption=caption+"</p>"
    // }
    else {
      var caption="<div style='max-height:200px; overflow-y:auto'> <p font='calibri' style='color:#4099FF'>Most Popular News Tweets:</p> ";
      var tweet="<p font='calibri'>"
      for (var i=0;i<data.result.news_tweets.length;i++) {
        tweet=data.result.news_tweets[i];
        prob=data.result.news_tweets_prob[i];
        if (!chopped.test(tweet)) {
          tweet=tweet.replace(http_regex,replacer);
        }
        caption=caption+"</br> "+tweet;
      };
      caption=caption+"</p>"

      caption=caption+"<p style='color:#4099FF'>Other Popular Tweets:</p> <p font='calibri'>";
      for (var i=0;i<data.result.other_tweets.length;i++) {
        tweet=data.result.other_tweets[i];
        prob=data.result.other_tweets_prob[i];
        if (!chopped.test(tweet)) {
          tweet=tweet.replace(http_regex,replacer);
        }
        caption=caption+"</br> "+tweet;
      };
      caption=caption+"</p> </div>"
    }
    console.log(caption)
    infowindow.setContent(caption);
    infowindow.open(map,marker);
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


