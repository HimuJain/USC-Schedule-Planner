jQuery(function ($) {
$(".course-info").ready(function(){
		//expanders
		$(".course-details").css({'display':'block'}).hide();
	});

	findterm = function() {
		const currentBody = document.querySelector('body');
		const t = currentBody.dataset.term;
		return t;
	}



	findsearch = function() {
		var m = window.location.href;
		n = m.indexOf("/search/");
		if(n && n != -1) {
			n = n+8;
			searchterm = m.substr(n);
			k = searchterm.indexOf('/');
			if(k && k != -1) {
				searchterm = searchterm.substr(0,k);
			}
		} else {
			n = m.indexOf("s=");
			if(n && n != -1) {
				n = n+2;
				searchterm = m.substr(n);
				k = searchterm.indexOf('/');
				if(k && k != -1) {
					searchterm = searchterm.substr(0,k);
				}
			}
		}
		return escape(searchterm);
	}

	$( function () {
		// homepage term inputs
		$("ul.terms li").on( "focusin", function() {
			termclass = $( this ).attr( "class" );
			if ( termclass.indexOf( 'active' ) === -1 ) {
				$( "li.active" ).removeClass( "active" );
				$( this ).addClass( "active" );
			}
		});

		function debounce(fn, delay) { // prevents repeatedly calling search function
			var timer = null;
			return function () {
				var context = this, args = arguments;
				clearTimeout(timer);
				timer = setTimeout(function () {
					fn.apply(context, args);
				}, delay);
			}
		}

		lastval = false;

		$(".search-string").on("keyup focus",debounce(function (e) { // autosuggest links if there's a match
			val = $(this).val();
			if(!lastval || val != lastval) {
				lastval = val;
				if( val.length > 2 ) {
					var term = $(this).prev("input").val();
					$(this).next(".autosuggest").load(base+'/match/?t='+encodeURIComponent(term)+'&search='+encodeURIComponent(val),function() {
						if( $(this).html() ) {
							$(this).fadeIn();
						} else {
							$(this).fadeOut();
						}
					});
				}
			} else if(lastval==val) {
				$(this).next(".autosuggest:hidden").fadeIn();
			}
		},200));

		autosugg = false;

		$(document).on("keydown",function(event) {
			if (!event) {
				event = window.event;
			}
			var code = event.keyCode;
			if (event.charCode && code == 0) {
				code = event.charCode;
			}

			if(($(".search-string").is(":focus") || $("a.match").is(":focus")) && (code == 38 || code == 40)) {
				event.preventDefault();
				clearTimeout(autosugg);
				switch(code) {
					case 38: // up.
						if( $(".autosuggest a.match:first-child").is(":focus") ) {
							$( "a.match:focus" ).parent(".autosuggest").prev(".search-string").focus();
							clearTimeout(autosugg);
						} else if( $(".autosuggest a").is(":focus") ) {
							$( document.activeElement ).prev("a").focus().addClass("focus");
							clearTimeout(autosugg);
						}
						break;
					case 40: // down.
						if( $(".search-string").is(":focus") ) {
							$(".search-string:focus").next().children("a:first-child").focus();
							clearTimeout(autosugg);
						} else if( $(".autosuggest a.match").not(":last-child").is(":focus") ) {
							$( document.activeElement ).next("a").focus().addClass("focus");
							clearTimeout(autosugg);
						}
						break;
				}
			}
		});

		$(document.activeElement).on("focusout",debounce(function(e) {
			var elclass = $(document.activeElement).attr("class");
				autosugg = setTimeout( function() {
					if( $(".search-string").is(":focus") || $("a.match").is(":focus") ) {
					} else {
						$(".autosuggest:visible").fadeOut();
					}
				}, 200 );
		},200));

		// program select behavior
		$(".program-select").on("change",function() {
			var thisoption = $(".program-select option:selected").val();
			var t = findterm();
			var currentterm = t;
			var basehref = window.location.origin;
			window.location.href = basehref+'/term-'+currentterm+'/classes/'+thisoption;
		});

		if( $('.chosen-select')[0] ) {
			var config = {
			  '.chosen-select'           : {},
			  '.chosen-select-deselect'  : {allow_single_deselect:true},
			  '.chosen-select-no-single' : {disable_search_threshold:10},
			  '.chosen-select-no-results': {no_results_text:'Oops, nothing found!'},
			  '.chosen-select-width'     : {width:"95%"}
			}
			for (var selector in config) {
			  $(selector).chosen(config[selector]);
			}
		}

		// term select behavior
		$(".term-select").on("change",function() {
			var thisoption = $(".term-select option:selected").val();
			var basehref = window.location.origin;
			basehref = basehref+'/term-'+thisoption;
			var programoption = $(".program-select option:selected").val();
			if(programoption) { basehref += '/classes/'+programoption+'/'; }
			window.location.href = basehref;

		});

		$("a.lightbox").each(function() {
			thishref = $(this).attr("href")+" #content-main";
			$(this).attr("href",thishref);
		});

		// search action rest-ify

		$("form[role=search]").on("submit",function() {
			searchterm = $(this).children("input[type=search").val();
			$(this).attr("action","/"+currentterm+"/search/"+escape(searchterm))
		});

		$("div.course-id, .detail-list h3").on("click",function(event) {
			event.preventDefault();
			t = this.parentNode.className;
			if(t.indexOf('expandable') != -1) {
				$(this.parentNode).removeClass("expandable").addClass("expanded");
			} else {
				$(this.parentNode).removeClass("expanded").addClass("expandable");
			}
			$(this.nextSibling).slideToggle(200);
		});

		//expand all
		$(".expand").on("click",function(event){
			event.preventDefault();
			$("div.course-details:hidden").slideDown("normal");
			$("div.expandable").removeClass("expandable").addClass("expanded");;
		});

		//collapse all
		$(".collapse").on("click",function(event){
			event.preventDefault();
			$("div.course-details:visible").slideUp("normal");
			$("div.expanded").removeClass("expanded").addClass("expandable");
		});

		//initially expanded course
		var ss = location.search.substring(1);

		if(ss) {
			exp = ss.indexOf('expand');
			if(exp != -1) {
				$(".course-details").slideDown("fast");
				$(".course-info").removeClass("expandable").addClass("expanded");
   			}
			op = ss.indexOf('c=');
			if(op != -1) {
				thiscourse = ss.substring(op+2).toUpperCase();
				if(thiscourse.indexOf('&') != -1) {
					thiscourse = thiscourse.substring(0,thiscourse.indexOf('&'));
					if(ss.indexOf('s=') != -1) {
		 			   thissection = ss.substring(ss.indexOf('s=')+2);
						if(document.getElementById(thissection)) {
							$("."+thissection).addClass("active");
			   				if(document.getElementById(thissection)) {
								$("."+thissection).addClass("active");
							}
						}
					}
				}
				if(document.getElementById(thiscourse)) {
					document.getElementById(thiscourse).className = "course-info expanded";
					$("#"+thiscourse+"-details").slideDown("normal",function() {
						coursey = document.getElementById(thiscourse).offsetTop-10;
			   			window.scrollTo(0,coursey);
					});
				}
			}
		}

		$(".course-info:only-child").removeClass("expandable").addClass("expanded");
		$(".course-info:only-child .course-details").slideDown("normal");

		if( $(".last")[0] ) {
			start = $(".last").html();
			currentterm = searchterm = '';
			findterm();
			currentterm = t;
			searchterm = findsearch();


			if(currentterm && searchterm) {
				if( $('.last').hasClass('end') || $(".searchresults p")[0] || $(".course-info").length < 20 ) {
					$('.showmore').hide();
				} else {
					$(".searchresults").after('<a class="showmore" href="/'+currentterm+'/search/'+searchterm+'/start/'+start+'/">Show more results</a>');
				}
			}
			$(".showmore").on("click",function(event) {
				event.preventDefault();
				var start = $(".last").html();
				$(".last").remove();
				$(".searchresults").append('<div class="start '+start+'" style="display:inline"></div>');
				$('.start.'+start).load("/"+currentterm+"/search/"+searchterm+"/start/"+start+"/content-only",function() {
					if($(".last").hasClass("end")) { $('.showmore').hide(); }
					var start = $(".last").html(); if(start==null) { $('.showmore').hide(); }
					$('.showmore').attr("href","/"+currentterm+"/search/"+searchterm+"/start/"+start+"/content-only");
				});
				lastcount = $('.start.'+start+' .course-info').length;
				if( lastcount < 20 ) {
					$('.showmore').hide();
				}
			});
		}

	// responsive tables

	var switched = false;
	var updateTables = function() {
		if (($(window).width() < 980) && !switched ){
			switched = true;
			$("table.responsive").each(function(i, element) {
				splitTable($(element));
			});
			return true;
		}
		else if (switched && ($(window).width() > 980)) {
			switched = false;
			$("table.responsive").each(function(i, element) {
				unsplitTable($(element));
			});
		}
	};

	$(window).load(updateTables);
	$(window).on("redraw",function(){switched=false;updateTables();}); // An event to listen for
	$(window).on("resize", updateTables);


	function splitTable(original)
	{
		original.wrap("<div class='table-wrapper' />");

		var copy = original.clone();
		copy.find("td:not(:first-child), th:not(:first-child)").css("display", "none");
		copy.removeClass("responsive");

		original.closest(".table-wrapper").append(copy);
		copy.wrap("<div class='pinned' />");
		original.wrap("<div class='scrollable' />");

		setCellHeights(original, copy);
	}

	function unsplitTable(original) {
		original.closest(".table-wrapper").find(".pinned").remove();
		original.unwrap();
		original.unwrap();
	}

	function setCellHeights(original, copy) {
		var tr = original.find('tr'),
				tr_copy = copy.find('tr'),
				heights = [];

		tr.each(function (index) {
			var self = $(this),
					tx = self.find('th, td');

			tx.each(function () {
				var height = $(this).outerHeight(true);
				heights[index] = heights[index] || 0;
				if (height > heights[index]) heights[index] = height;
			});

		});

		tr_copy.each(function (index) {
			$(this).height(heights[index]);
		});
	}


	});
});