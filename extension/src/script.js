"use strict";

function annotate() {
  var url = window.location.href;
  var text = "";
  var words = [];
  var re = /[\w_\-]+/g;

  // console.log(url)
  // console.log(new RegExp('http://www.plosbiology.org/article/*').test(url))

  if (new RegExp('http://.*plos.*\.org/article/*').test(url)) {
    text = $(".article").text();
  }

  var match;
  
  do {
    match = re.exec(text);
    if (match) {
      words.push(match[0]);
    }
  } while (match);

  // console.log(words);

  if (words.length > 0)
    // send text to servers
    $.ajax( {
      type: "POST",
      url: "http://bioannotator.kevinformatics.com/annotate",
      dataType: "json",
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({words: words}),
      success: function(data) { 
        // console.log(data);
        $("div").highlight(Object.keys(data), { wordsOnly: true, caseSensitive: true, className: 'bioannotator-highlight' });
        $("body div span.bioannotator-highlight").popover( { placement: 'top', html: true, content: function() { 
          var gene = $(this).text();
          var linkStr  = ""
          var linkData = { 
                       "wikipedia": { "icon": chrome.extension.getURL("img/icon-wikipedia.png"), "url": function(gene) { return ["http://en.wikipedia.org/wiki/", gene].join("") } },
                       "refseq"   : { "icon": chrome.extension.getURL("img/icon-dna.svg"),       "url": function(gene) { return 'refseq' in data[gene] ? ["http://www.ncbi.nlm.nih.gov/nuccore/?term=", data[gene]["refseq"], "+AND+srcdb_refseq%5BPROP%5D"].join("") : false } },
                       "pubmed"   : { "icon": chrome.extension.getURL("img/icon-book.svg"),       "url": function(gene) { return 'pubmed' in data[gene] ? ["http://www.ncbi.nlm.nih.gov/pubmed/?term=", data[gene]["pubmed"].replace(", ", "+")].join("") : false } },
                       "biogps"   : { "icon": chrome.extension.getURL("img/icon-gps.svg"),       "url": function(gene) { return  ["http://biogps.org/?query=", gene, "#goto=welcome"].join("") } },
                     };
          for (var key in linkData) {
            if (!linkData[key]["url"](gene)) {
              continue;
            }
            var icon = $("<img>").attr("src", linkData[key]["icon"]).addClass("bioannotator-icon");
            var link = $("<a></a>").attr("href",  linkData[key]["url"](gene)).attr("target", "_blank").append(icon);
            linkStr += link.prop('outerHTML');
          }
          return linkStr;
        } });
      }
    });
}

annotate();
