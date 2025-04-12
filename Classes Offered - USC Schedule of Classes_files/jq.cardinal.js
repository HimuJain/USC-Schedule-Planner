jQuery(document).ready(function( $ ) {
	// append icons for links to non-web filetypes (email, pdf, doc, xls, ppt, etc)
	$("a[href^='mailto:']").addClass("email");
	$("a[href$='.pdf']").addClass("pdf");
	$("a[href$='.xls']").addClass("xls");
	$("a[href$='.ppt']").addClass("ppt");
	$("a[href$='.doc'], a[href$='.txt'], a[href$='.rft']").addClass("txt");

	$("#content-main img, #content-sub img").removeAttr("width").removeAttr("height");

	// handle nav for touch-enabled devices with small screens
	if ('ontouchstart' in document) {
		$("#nav").prepend('<a href="#nav" id="navtoggle">Show Navigation</a>');
		$("#navtoggle").on('click', function() {
			var menu = $(".menu");
			if (menu.hasClass("show")) {
				menu.removeClass("show");
				$(this).text("Show Navigation");
			} else {
				menu.addClass("show");
				$(this).text("Hide Navigation");
			}
			return false;
		});
	}
	$('iframe[src^="https://www.youtube.com"]').removeAttr("width").removeAttr("height").wrap('<div class="vidwrap"></div>');

});
