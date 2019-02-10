function isDebugging() {
  return false;
}

$(document).on('pagebeforeshow', '#index', function(){ 
  $('<input id="progressbar">').appendTo('[ data-role="content"]').attr({'name':'slider','id':'slider','data-highlight':'true','min':'0','max':'100','value':'50','type':'range'}).slider({
      create: function( event ) {
          $(this).parent().find('input').hide();
          $(this).parent().find('input').css('margin-left','-9999px'); // Fix for some FF versions
          $(this).parent().find('.ui-slider-track').css('margin','0 15px 0 15px').css('pointer-events','none');
          $(this).parent().find('.ui-slider-handle').hide();
      }
  }).slider("refresh");   
  progressBar.setValue('#slider', 0);
  //$("input#slider.ui-slider-input").remove();
  //$(".ui-slider-handle").remove();
  //$('.ui-slider-track').css('margin','0 15px 0 15px').css('pointer-events','none');
});

var progressBar = {
  setValue:function(id, value) {
      $(id).val(value);
      $(id).slider("refresh");
  }
}

function getCheckedBoxes(chkboxName) {
  var checkboxes = document.getElementsByName(chkboxName);
  var checkboxesChecked = [];
  for (var i=0; i<checkboxes.length; i++) {
     if (checkboxes[i].checked) {
        checkboxesChecked.push(checkboxes[i]);
     }
  }
  return checkboxesChecked;
}

function getTextNextToCheckedBoxes(chkboxName, textBoxNames) {
  var checkboxes = document.getElementsByName(chkboxName);
  var textBoxes = document.getElementsByName(textBoxNames);
  var checkedTexts = [];
  // loop over them all
  for (var i=0; i<checkboxes.length; i++) {
     // And stick the checked ones onto an array...
     if (checkboxes[i].checked) {
      checkedTexts.push(textBoxes[i]);
     }
  }
  return checkedTexts;
}

function toggleAllCheckboxes(source) {
  checkboxes = document.getElementsByName('checkbox');
  for(var i=0, n=checkboxes.length;i<n;i++) {
    checkboxes[i].checked = source.checked;
  }
}

$(window).on("load", function() {
  $("#toggle_all").on('click', function () {
    $("[name='checkbox']").prop('checked', $(this).is(":checked")).checkboxradio('refresh');
  })
  $("#button").on('click', function () {
    disableControls();
    begin(null, $(this).data("user-id"), $(this).data("token-id"));
  })
});

function createXHR() {
  try {
      return new XMLHttpRequest();
  } catch (e) {
      try {
          return new ActiveXObject("Microsoft.XMLHTTP");
      } catch (e) {
          return new ActiveXObject("Msxml2.XMLHTTP");
      }
  }
}

function disableControls() {
  $("#button").prop('disabled', true);
  $('input[name=checkbox]').prop('disabled', true);
}

function enableControls() {
  $("#button").prop('disabled', false);
  $('input[name=checkbox]').prop('disabled', false);
}

function begin(source, userId, tokenId) {
  progressBar.setValue('#slider', 0);
  let checkBoxes = getCheckedBoxes("checkbox");
  let textBoxes = getTextNextToCheckedBoxes("checkbox", "status_message");
  for (let ix = 0; ix < textBoxes.length; ix += 1) {
    textBoxes[ix].innerHTML = "";
  }
  let arrayLength = checkBoxes.length;
  if (arrayLength == 0) {
    console.log("No albums selected");
    enableControls();
    return;
  } else {
    console.log("Beginning sort operation");
  }

  let requestIx = 0;
  let prepareNextCall = null;
  let retriesMax = 5;
  let retriesLeft = retriesMax;
  let onCallFinished = function() {
    if (this.readyState == 4) {
      let obj = null;
      let ouputMessage = textBoxes[requestIx];
      let retrying=false;
      if (this.status == 200) {
        try {
          obj = JSON.parse(this.responseText);
          retriesLeft = retriesMax;
        } catch (e) {
          retriesLeft -= 1;
          if (retriesLeft > 0) {
            obj = JSON.parse('{ "result" : "error", "error_message" : "Retrying..."}');
            retrying = true;
          } else {
            obj = JSON.parse('{ "result" : "error", "error_message" : "Script error"}');
            if (isDebugging()) {
              console.log(this.responseText);
            }
          }
        }
      } else {
        //console.log("Request failed with HTTP error: " + this.status);
        retriesLeft -= 1;
        if (retriesLeft > 0) {
          obj = JSON.parse('{ "result" : "error", "error_message" : "Retrying..."}');
        } else {
          obj = JSON.parse('{ "result" : "error", "error_message" : "HTTP error"}');
          if (isDebugging()) {
            console.log(this.responseText);
          }
        }
      }
      if (obj["result"] === "success") {
        if ("message" in obj) {
          ouputMessage.innerHTML = obj["message"];
        } else {
          ouputMessage.innerHTML = "Success";
        }
      } else {
        if ("error_message" in obj) {
          ouputMessage.innerHTML = "Error, " + obj["error_message"];
        } else {
          ouputMessage.innerHTML = "Error, unknown reason";
        }
      }
      if (!retrying) {
        requestIx += 1;
      } 
      progressBar.setValue('#slider', 100.0 * ((requestIx) / arrayLength));
      if (requestIx < arrayLength)
        prepareNextCall(userId, tokenId, checkBoxes[requestIx].id);
      else
        enableControls();
    }
  }
  prepareNextCall = function(userId, tokenId, albumId) {
    var xhttp = createXHR();
    xhttp.onreadystatechange = onCallFinished;
    xhttp.open("GET", "sort-album.py?userId=" + userId + "&tokenId=" + tokenId + "&albumId=" + albumId, true);
    xhttp.send();  
  };
  prepareNextCall(userId, tokenId, checkBoxes[requestIx].id);
}
