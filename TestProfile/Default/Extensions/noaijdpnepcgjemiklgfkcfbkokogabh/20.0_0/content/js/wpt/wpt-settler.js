var isScrolling;
try {
	RESTORE=0;
        var ext = FExtension.browserInject;
	unloadScript();

	if(self == top)	WPT_RUN();


} catch(ex){}

function unloadScript() {
    var DOMAIN = location.host.toString();
    var s = document.getElementsByTagName("script");
    for(var i=0; i<s.length; i++){
	if(s[i].id == "SL_WPT"){
		document.head.removeChild(s[i]);

		if(self != top){
			if(DOMAIN.indexOf(".yahoo.")==-1){
				//location.reload();
			}
		}

	}
    }    
}


window.addEventListener('scroll', function ( event ) {
	window.clearTimeout( isScrolling );
	isScrolling = setTimeout(function() {
//		if(RESTORE==0)	WPT_MUTATION();
		if(RESTORE==0)	WPT_RUN();
	}, 50);
}, false);


