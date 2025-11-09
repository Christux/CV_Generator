(function() {
    'use strict';

    if(!bambo.version || bambo.version < 1.4) {
        throw new Error('The app needs BamboJS > v1.4');
    }
    
    bambo.module('scroll', ['$dom', '$scroll', '$location', function($dom, $scroll, $location){
    
        var menuItems, categories;
        var selectedCategory;
    
        /*
        * Listens to scroll event
        */
        $scroll.registerHandler(function (position, pageHeight, screenHeight) {
            displaySelectedCategory(position, pageHeight, screenHeight);
        });
    
        return {
            $init: function() {
                menuItems = $dom.select('.mb-menu-item');
                categories = $dom.select('.category');
            },
            $build: function() {
    
                var cat = $location.getAnchor() || 'accueil';
    
                categories.forEach(function(category){
                    if(category.id() == cat) {
                        render(category);
                    }
                });
    
                if(cat !=='accueil') {
                    scrollTo(cat);
                }
            }
        }
    
        function displaySelectedCategory(position, pageHeight, screenHeight) {
    
            var y = position + Math.ceil(screenHeight / 3.0);
    
            categories.forEach(function(category) {
                
                if(y >= category.offsetTop() && y < category.offsetBottom()) {
                    
                    if(selectedCategory !== category) {
                        render(category);
                    }
                }
            });
        }
    
        function render(category) {
    
            selectedCategory = category;
    
            // Reset buttons
            menuItems.removeClass('active');
            menuItems.css('pointerEvents', 'auto');
    
            // Show selected caterogy
            menuItems.forEach(function(item) {
    
                if(item.hasClass(category.id())) {
                    item.addClass('active');
                    item.css('pointerEvents', 'none');
                    $location.setWhithoutMove(category.id());
                }
            });
        }
    
        function scrollTo(hash) {
            //location.hash = "#" + hash;
            $location.set(hash);
        }
    
    }]);
    
    
    /*
     * Hide headerbar module
     */
    bambo.module('hideHeader', ['$dom', '$scroll', function hideHeader($dom, $scroll) {
    
        /*
         * Handles headerbar visibility
         */
        var entete, menu, corps;
        var enteteHeight, padding;
        var isCollapsed = false;
    
        return (function () {
    
            /*
            * Listens to scroll event
            */
            $scroll.registerHandler(function (position) {
                render(position);
            });
    
            return this;
        }).call({
            $init: function () {
                entete = $dom.select('#header');
                menu = $dom.select('#menu');
                corps = $dom.select('#contenu');
    
                measureHeaderHeight();
                padding = enteteHeight + menu.nativeElement.getBoundingClientRect().height; //.offsetHeight;

                window.addEventListener('resize', measureHeaderHeight);
                window.addEventListener('orientationchange', measureHeaderHeight);
            },
            $build: function() {
                render($scroll.get());
            },
            resetScroll: function () {
                if (isCollapsed) {
                    $scroll.set(enteteHeight);
                }
            }
        });
    
        //------------------------------------------------------------------
        function measureHeaderHeight() {
            enteteHeight = entete.nativeElement.getBoundingClientRect().height; //offsetHeight;
        }

        /*
        * Hides headerbar
        */
        function collapse() {
            isCollapsed = true;
            entete.hide();
            menu.css('position', 'fixed');
            corps.css('padding-top', padding.toString() + 'px');
            
        }
    
        /*
        * Unhides headerbar
        */
        function rise() {
            isCollapsed = false;
            entete.show();
            menu.css('position', 'static');
            corps.css('padding-top', '0px');
            
        }
    
        /*
        * Decides to hide or unhide according to scroll position
        */
        function render(y) {
    
            if (y > enteteHeight && !isCollapsed) {
                collapse();
            }
    
            if (y < enteteHeight && isCollapsed) {
                rise();
            }
        }
    }]);
    
    /*
     * Some cool effects
     */
    bambo.module('coolStuff', ['$dom', '$scroll', function($dom, $scroll){
    
        var enteteHeight;
    
        $scroll.registerHandler(function (position) {
            render(position);
        });
    
        return {
            $init: function() {
                enteteHeight = $dom.select('#header').nativeElement.offsetHeight;
            }
        };
    
        function render(position) {
            $dom.select('#photo').css('transform','rotate('+(position/enteteHeight)+'rad)')
        }
    }]);
    
    
    /*
     * Konami easter egg, convert text to leet :)
     */
    bambo.module('easterEgg', ['$dom', '$konami', '$leet','$nyan', function ($dom, $konami, $leet, $nyan) {
    
        var count = 0;
    
        return {
            $final: function () {
                $konami.registerHandler(function () {
    
                    if(count === 0) {
                        $leet.run();
                        $dom.select('#photo').nativeElement.src = "img/unicorn.png";
                    }
                    else {
                        $nyan.run();
                    }
                    count++;
                });
            }
        }
    }]);
    
    bambo.module('caroussel', ['$dom', function($dom){
    
        var caroussels;
    
        return {
            $init: function() {
                caroussels = $dom.select('caroussel');
            },
            $build: function() {
                caroussels.forEach(function(caroussel){
                    carousselFactory(caroussel);
                });
            }
        };
    
        function carousselFactory(carousselElement) {
    
            var interval = carousselElement.attribute('interval');
            var items = carousselElement.select('.caroussel-item');
            var i = 0, l = items.count();
            var run = true;
    
            carousselElement.click(function(){
                next();
            });
    
            carousselElement.mouseover(function(){
                run = false;
            });
    
            carousselElement.mouseleave(function(){
                run = true;
            });
    
            setInterval(function(){
                if(run) {
                    next();
                }
            }, interval);
    
            function next() {
    
                items.addClass('hidden');
    
                items.forEach(function(item, idx) {
                    
                    if(idx === i) {
                        item.removeClass('hidden');
                    }

                    // Lazy load next picture
                    if(idx === i + 1) {
                        var lazySrc = item.attribute('data-src');

                        if(lazySrc !== null) {
                            item.nativeElement.removeAttribute('data-src');
                            item.nativeElement.setAttribute('src', lazySrc);
                        }
                    }
                });
    
                i = (i === l - 1) ? 0 : i + 1;
            }
        }
    }]);
    
    bambo.module('showMore', ['$dom', function($dom){
    
        var categories;
    
        return {
            $init: function() {
                categories = $dom.select('.category');
            },
            $build: function() {
    
                categories.forEach(function(categoryElement){
    
                    var showMoreBtn = categoryElement.select('.show-more');
                    var items = categoryElement.select('.item');
    
                    if(showMoreBtn.count() > 0) {
                        showMoreBtn.click(function(btn){
                            btn.hide();
                            items.show();
                        });
                    }
                });
            }
        };
    }]);

    bambo.module('checkOverflow', ['$dom', function($dom){

        return {
            $final: function() {
    
                var root = $dom.select('body').first().nativeElement;
            
                discoverDOM(root, function(element){        
            
                    if(isOverflown(element))
                    {
                        element.style.backgroundColor = 'red';
                    }
                });
    
            }
        };
    
        function isOverflown(element) {
            return element.scrollHeight > element.clientHeight || element.scrollWidth > element.clientWidth;
        }
        
        function discoverDOM(elem, callback) {
        
            if(bambo.isObject(elem))
            {
                callback(elem);
        
                for (var i = 0, l = elem.children.length; i < l; i++) {
                    discoverDOM(elem.children[i], callback);
                }
            }
        }
    
    }], false);

})();
