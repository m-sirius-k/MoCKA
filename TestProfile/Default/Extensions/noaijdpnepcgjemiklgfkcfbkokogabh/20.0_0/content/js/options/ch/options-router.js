(function(){
    window.addEventListener('load',function(){
	GEBI('SL_translate_container').style.opacity="1";
	CONSTRUCTOR();
    },!1);
})();

function CONTRIBUTIN(){
  GEBI("d0").href="https://imtranslator.net"+_CGI+"&a=0";
}

function CONSTRUCTOR(){
        CONTRIBUTIN();
	var manifestData = chrome.runtime.getManifest();
	GEBI('SL_h3').innerText="v."+manifestData.version;  
	GEBI('SL_h2').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTITLE')));
//	GEBI('SL_PP').title=FExtension.element(GET("SL_LOCALIZATION"),'extContribution_ttl');
	GEBI('SL_BG').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extChTrApp')));
}
function GEBI(id){ return document.getElementById(id);}