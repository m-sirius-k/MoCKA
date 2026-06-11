var MSKEY = "0";
var PLATFORM = "Chrome";
var EXPORT_EXT = " SL";
var GLOB_PREF = "SL";
var GLOB_CNTR = 2;


//var PLATFORM = "Opera";
//var EXPORT_EXT = " SL";
//var GLOB_PREF = "SL";
//var GLOB_CNTR = 3;



//for GT only
//var PLATFORM = "Opera";
//var EXPORT_EXT = " GT";
//var GLOB_PREF = "SLG";
//var GLOB_CNTR = 4;



//var SL_GEO = new Array ("com","es","de","it","fr","rs","pn","ps","sn","so");
var SL_GEO = new Array ("com");
var DET = 0;
// 0 - G
// 1 - SL
var _TP = "chr-ImTranslator"
var _FOLDER = "extensions";
var _CGI = "/"+_FOLDER+"/?tp="+_TP;

var reservedHK = "_HK_bb1,_HK_bb2,_HK_btn,_HK_gt1,_HK_gt2,_HK_it1,_HK_it2,_HK_opt,_HK_wpt1,_HK_wpt2,_change_lang_HK_it,_HK_SO_wpt,_HK_CT_wpt";
var SL_TTS = "en,es,ru,de,pt,fr,it,ko,ja,zh-CN,zh-TW,en-gb,fr-CA,lzh,pt-PT";             
var G_TTS = "ar,cs,da,nl,fi,el,hi,hu,no,pl,sk,sv,th,tr,la,bn,id,km,uk,vi";
    G_TTS = G_TTS+","+SL_TTS;

var LISTofPRpairsDefault=",af,ak,am,ar,as,ay,az,ba,be,bg,bho,bm,bn,bo,bs,ca,ceb,ckb,co,cs,cv,cy,da,de,doi,dsb,dv,ee,el,emj,en,en-gb,eo,es,et,eu,fa,fi,fj,fo,fr,fr-CA,fy,ga,gd,gl,gn,gom,gu,ha,haw,hi,hmn,hr,hsb,ht,hu,hy,id,ig,ikt,ilo,is,it,iu,iu-Latn,iw,ja,jw,ka,kazlat,kk,km,kn,ko,kri,ku,ky,la,lb,lg,ln,lo,lt,lug,lus,lv,lzh,mai,mg,mhr,mi,mk,ml,mn,mni-Mtei,mn-Mong,mr,mrj,ms,mt,my,ne,nl,no,nso,ny,nya,om,or,otq,pa,pap,pl,prs,ps,pt,pt-PT,qu,ro,ru,run,rw,sa,sah,sd,si,sk,sl,sm,sn,so,sq,sr,sr-Latn,srsl,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tlh-Latn,tlsl,tn,to,tr,ts,tt,ty,udm,ug,uk,ur,uz,uzbcyr,vi,xh,yi,yo,yua,yue,zh-CN,zh-TW,zu";
var LISTofPR = new Array ("Google","Microsoft","Translator","Yandex");
var LISTofLANGsets = new Array (",af,ak,am,ar,as,ay,az,be,bg,bho,bm,bn,bs,ca,ceb,ckb,co,cs,cy,da,de,doi,dv,ee,el,en,eo,es,et,eu,fa,fi,fr-CA,fr,fy,ga,gd,gl,gn,gom,gu,ha,haw,hi,hmn,hr,ht,hu,hy,id,ig,ilo,is,it,iw,ja,jw,ka,kk,km,kn,ko,kri,ku,ky,la,lb,lg,ln,lo,lt,lus,lv,mai,mg,mi,mk,ml,mn,mni-Mtei,mr,ms,mt,my,ne,nl,no,nso,ny,om,or,pa,pl,ps,pt,pt-PT,qu,ro,ru,rw,sa,sd,si,sk,sl,sm,sn,so,sq,sr,srsl,st,su,sv,sw,ta,te,tg,th,ti,tk,tl,tlsl,tr,ts,tt,ug,uk,ur,uz,vi,xh,yi,yo,zh-CN,zh-TW,zu",",af,am,ar,as,az,ba,bg,bho,bn,bo,bs,ca,ckb,cs,cy,da,de,dsb,dv,el,en,en-gb,es,et,eu,fa,fi,fj,fo,fr,fr-CA,ga,gl,gom,gu,ha,hi,hmn,hr,hsb,ht,hu,hy,id,ig,ikt,is,it,iu,iu-Latn,iw,ja,ka,kk,km,kn,ko,ku,ky,ln,lo,lt,lug,lv,lzh,mai,mg,mi,mk,ml,mn,mn-Mong,mr,ms,mt,my,ne,nl,no,nso,nya,or,otq,pa,pl,prs,ps,pt,pt-PT,ro,ru,run,rw,sd,si,sk,sl,sm,sn,so,sq,sr,sr-Latn,srsl,st,sv,sw,ta,te,th,ti,tk,tl,tlh-Latn,tlsl,tn,to,tr,tt,ty,ug,uk,ur,uz,vi,xh,yo,yua,yue,zh-CN,zh-TW,zu",",af,am,ar,az,ba,be,bg,bn,bs,ca,ceb,cs,cv,cy,da,de,el,emj,en,eo,es,et,eu,fa,fi,fr,ga,gd,gl,gu,hi,hr,ht,hu,hy,id,is,it,iw,ja,jv,ka,kazlat,kk,km,kn,ko,ky,la,lb,lo,lt,lv,mg,mhr,mi,mk,ml,mn,mr,mrj,ms,mt,my,ne,nl,no,pa,pap,pl,pt,ro,ru,sah,si,sk,sl,sq,sr,sr-Latn,srsl,su,sv,sw,ta,te,tg,th,tl,tlsl,tr,tt,udm,uk,ur,uz,uzbcyr,vi,xh,yi,zh-CN,zu",",af,am,ar,az,ba,be,bg,bn,bs,ca,ceb,cs,cv,cy,da,de,el,emj,en,eo,es,et,eu,fa,fi,fr,ga,gd,gl,gu,hi,hr,ht,hu,hy,id,is,it,iw,ja,jv,ka,kazlat,kk,km,kn,ko,ky,la,lb,lo,lt,lv,mg,mhr,mi,mk,ml,mn,mr,mrj,ms,mt,my,ne,nl,no,pa,pap,pl,pt,ro,ru,sah,si,sk,sl,sq,sr,sr-Latn,srsl,su,sv,sw,ta,te,tg,th,tl,tlsl,tr,tt,udm,uk,ur,uz,uzbcyr,vi,xh,yi,zh-CN,zu");
                                  
var LISTofPRpairs = new Array ();


for (var SL_I = 0 ; SL_I < LISTofPR.length; SL_I++){
    switch(LISTofPR[SL_I]){
	case "Google": LISTofPRpairs[SL_I]=LISTofLANGsets[0];break;
	case "Microsoft": LISTofPRpairs[SL_I]=LISTofLANGsets[1];break;
	case "Translator": LISTofPRpairs[SL_I]=LISTofLANGsets[2];break;
	case "Yandex": LISTofPRpairs[SL_I]=LISTofLANGsets[3];break;
    }	
}

var DO_NOT_TRUST_WORD = "be,bg,mk,sr,kk,mn,tg";
var DO_NOT_TRUST_TEXT = "zh";

var ImTranslator_theurl = "https://imtranslator.net/";

var FExtension = {
	config: {
		debugIsEnabled: true
	},

	extend: function(parentPrototype, child) {
		function CloneInternal(){};
		CloneInternal.prototype = parentPrototype;
		child.prototype.constructor = child;
		return new CloneInternal();
	},

	AddHtmlToObj: function(obj,tag,htm){
	      var container = GEBI(obj);
		while (container.firstChild) {
		  container.removeChild(container.firstChild);
		}
	      var eUL = document.createElement(tag);
	      var st = document.createAttribute("src");
	      st.value = htm;
	      eUL.setAttributeNode(st);
      	container.appendChild(eUL); 
	},

	element: function(loc,msg){
		return SL_SETCHROMELOC(msg,loc);
	}

       		
};

FExtension.alert_debug = function(msg) {
//	if (FExtension.config.debugIsEnabled)
//		window.alert(msg);
};


function SL_SETCHROMELOC(name,CLloc){
    if(chrome.i18n.getUILanguage()){
	 var BRloc=chrome.i18n.getUILanguage();
	 name=name.replace("ext","_");
	 if(BRloc==CLloc){
	  var BRloc=BRloc.substr(0,2);
	  return chrome.i18n.getMessage(BRloc+name);
	 } else { 
		return chrome.i18n.getMessage(CLloc+name);
	 }	
    }
}


function SL_isLinux() {
        var OSName = false;
	if (navigator.appVersion.indexOf("X11")!=-1) OSName=true;
	if (navigator.appVersion.indexOf("Linux")!=-1) OSName=true;
	return OSName;
}

