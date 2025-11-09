/*!
BamboJS

Description : Light javascript module builder
Author : Christophe Rubeck
Version : 1.5
Date : 2018 oct 23
See : https://github.com/Christux/BamboJS


Description :
-------------

	The library is designed for modules building thanks to dependency injection.
	A module is therefore a singleton (instanciate once).
	Dependency modules are automatiquely instanciated.

	After module instanciation, the boot sequence is launched.
	All $init are run (see module template), then all $build, then all $final.


Usage :
-------

	- module(name, constructor, loadOnStartup)
		name: string
		constructor: function that returns an object
		loadOnStartup: boolean, default true

	- forEach(array, callback)
		array: array or object (loop on properties)
		callback: function that loops ont all elements

	- isString(item)
	- isObject(item)
	- isArray(item)
	- isFunction(item)
	- isBoolean(item)
	- isNumber(item)
	- isUndefinedOrNull(item)


Module template :
-----------------

	bambo.module(['dep1','dep2', function(dep1, dep2) {

		return {
			$init: function() {
			},
			$build: ['dep3', function(dep3) {
			}],
			$final: function() {
			},
			method1: function() {
			},
			method2: function() {
			},
			etc.
		};
	}]);

	$init, $build and $final methods are optional.
*/


(function (context) {
	'use strict';

	if (context.hasOwnProperty('bambo'))
		throw new Error('Library BamboJS is already loaded !');
	else
		context.bambo = BamboCoreFactory();

	//////////////////// BAMBO ///////////////////////////////////////
	function BamboCoreFactory() {

		var injector = injectorFactory();

		return (function () {

			/*
			* Initialize all sub-object
			*/
			var init = execStep("$init");
			var build = execStep("$build");
			var final = execStep("$final");

			var boot = function() {
				// Load statups module and their dependencies
				instanciate();

				// Module boot sequence
				init();
				build();
				final();
			};

			/*
			* Waits until all module constructors are loaded before to init
			*/
			window.addEventListener(
				"load",
				(function () {
					return function () {
						boot();
					}
				})(),
				false);

			this.boot = function() {
				boot();
			};

			return this;

		}).call({
			module: function (name, constructor, loadOnStartup) {

				if (!isString(name) || name === '')
					throw new Error('Module name must be a string');

				injector.register(name, constructor, isBoolean(loadOnStartup) ? loadOnStartup : true);

				return this;
			},
			isString: function(val) {
				return isString(val);
			},
			isObject: function(val) {
				return isObject(val);
			},
			isArray: function(val) {
				return isArray(val);
			},
			isFunction: function(val) {
				return isFunction(val);
			},
			isBoolean: function(val) {
				return isBoolean(val);
			},
			isNumber: function(val) {
				return isNumber(val);
			},
			isUndefinedOrNull: function(val) {
				return isUndefinedOrNull(val);
			},
			forEach: function(array, callback) {
				forEach(array, callback);
			},
			version: 1.5
		});

		//------------------------------------------------------------------------

		function instanciate() {
			injector.forEachModules(function (module) {
				if (module.loadOnStartup()) {
					module.getInstance();
				}
			});
		}

		function execStep(step) {
			return function () {
				injector.forEachModules(function (module) {

					if (module.isInstanciated()) {
						var obj = module.getInstance();

						if (obj.hasOwnProperty(step)) {
							injector.resolve(obj[step]);
						}
					}
				});
			};
		}
	}

	/////////////////////// Utils ///////////////////////////////////////////
	function isObject(val) {
		return (typeof val === 'object' && !Array.isArray(val) && val !== null);
	}

	function isArray(val) {
		return Array.isArray(val);
	}

	function isString(val) {
		return typeof val === 'string';
	}

	function isFunction(val) {
		return typeof val === 'function';
	}

	function isBoolean(val) {
		return typeof val === 'boolean';
	}

	function isNumber(val) {
		return typeof val === 'number';
	}

	function isUndefinedOrNull(val) {
		return typeof val === 'undefined' || val === null;
	}

	function forEach(array, callback) {

		if (!isObject(array) && !isArray(array)) {
			throw new Error('First parameter must be an array or an object');
		}

		if (!isFunction(callback)) {
			throw new Error('Second parameter must be a function');
		}

		if (isArray(array)) {
			for (var i = 0, l = array.length; i < l; i++) {
				callback(array[i], i);
			}
		}

		if (isObject(array)) {
			var i = 0;
			for (var pptName in array) {
				if (array.hasOwnProperty(pptName)) {
					callback(array[pptName], i++);
				}
			}
		}
	}

	///////////////// INJECTOR //////////////////////////
	function injectorFactory() {

		var modules = {};

		return (function () {

			/*
			 * Registration of itself
			 */

			modules['$injector'] = singletonFactory('$injector', null, false, this);

			return this;

		}).call({

			/*
			 * Public methods
			 */

			register: function (name, constructor, loadOnStartup) {
				addModule(name, singletonFactory(name, constructor, loadOnStartup || false));
			},
			resolve: function (func, deps, extDependencies) {
				return resolve(func, deps, modules, extDependencies, 0);
			},
			forEachModules: function (callback) {

				forEach(modules, function (module) {
					callback.apply(this, [module]);
				});
			}
		});

		//-----------------------------------------------------------

		function singletonFactory(name, constructor, loadOnStartup, instance) {

			var instance = instance || undefined;

			return {
				getInstance: function (recursionLevel) {

					if (!isInstanciated()) {
						instance = instanciate(recursionLevel);
					}
					return instance;
				},
				isInstanciated: function () {
					return isInstanciated();
				},
				loadOnStartup: function () {
					return loadOnStartup;
				}
			};

			//-----------------------------
			function isInstanciated() {
				return isObject(instance);
			}

			function instanciate(recursionLevel) {

				var recursionLevel = isNumber(recursionLevel) ? recursionLevel + 1 : 0;

				var obj = resolve(constructor, [], modules, {}, recursionLevel);

				if (!isObject(obj)) {
					throw new Error('Module ' + name + ' constructor is not correctly defined, it must return an object');
				}

				return obj;
			}
		}

		function addModule(name, obj) {

			if (modules.hasOwnProperty(name)) {
				throw new Error('Module ' + name + ' is already registered');
			}

			modules[name] = obj;
		}

		function resolve(func, deps, intDependencies, extDependencies, recursionLevel) {

			// Avoid infinite loop in module instanciation
			if (recursionLevel > 1000)
				throw new Error('Loop in module dependencies detected');

			// Array format
			if (isArray(func)) {
				var array = func;
				var func = array[array.length - 1];
				var deps = array.slice(0, array.length - 1);

				if (!isFunction(func))
					throw new Error('Last element must be a function');
			}
			else {
				var deps = deps || [];

				if (func.hasOwnProperty('$inject')) {

					deps = func.$inject;

					if (!isArray(deps))
						throw new Error('$inject parameter must be an array');
				}
			}

			if (!isFunction(func))
				throw new Error('First element must be a function');

			if (!isArray(deps))
				throw new Error('Dependency parameter must be an array of strings');

			return factory(func, getModules(deps, intDependencies || {}, extDependencies || {}, recursionLevel));
		}


		function getModules(deps, intDependencies, extDependencies, recursionLevel) {
			var mods = [];

			forEach(deps, function (dep) {

				if (!isString(dep))
					throw new Error('Dependency must be a string');

				if (intDependencies.hasOwnProperty(dep)) {
					mods.push(intDependencies[dep].getInstance(recursionLevel));
				} else {
					if (extDependencies.hasOwnProperty(dep)) {
						mods.push(extDependencies[dep]);
					} else {
						throw new Error('Dependency module ' + dep + ' not found !');
					}
				}
			});
			return mods;
		}

		function factory(func, mods) {
			return func.apply(this, mods);
		}
	}

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$http', httpModuleFactory, false);

	var isFunction = ctx.bambo.isFunction;
	var isString = ctx.bambo.isString;

	function httpModuleFactory() {

		return {
			get: function (url) {

				if (!isString(url))
					throw new Error('Url must be a string');

				return xhrFactory('GET', url, null);
			},
			post: function (url, obj) {

				if (!isString(url))
					throw new Error('Url must be a string');

				return xhrFactory('POST', url, obj);
			}
		};
	}

	function xhrFactory(verb, url, obj) {

		var xhr = new XMLHttpRequest();
		var success, error, timeout;
		var obj = obj || null;

		return (function () {

			xhr.onreadystatechange = function () {

				if (xhr.readyState === xhr.DONE) {
					if (xhr.status === 200) {
						if (success) {
							if (isFunction(success)) {
								success(xhr.responseText);
							}
						}
					} else {
						if (error) {
							if (isFunction(error)) {
								error(xhr.status + ' ' + xhr.statusText);
							}
						}
					}
				}
			};

			xhr.onerror = function (e) {
				if (error) {
					if (isFunction(error)) {
						error(e.error);
					}
				}
			};

			xhr.ontimeout = function (e) {
				if (timeout) {
					if (isFunction(timeout)) {
						timeout(e);
					}
				}
			};

			return this;

		}).call({
			success: function (callback) {
				success = callback;
				return this;
			},
			error: function (callback) {
				error = callback;
				return this;
			},
			timeout: function (callback) {
				timeout = callback;
				return this;
			},
			setTimeout: function (delay) {
				xhr.timeout = delay;
				return this;
			},
			send: function () {
				xhr.open(verb, url, true);
				xhr.send(obj);
			}
		});
	}

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$konami', ['$observer', konamiModuleFactory], false);

	function konamiModuleFactory($observer) {

		var pattern = "38384040373937396665";
		var input = "";
		var observer = $observer.create();
		var timer = null;

		return (function () {

			window.document.addEventListener("keydown", function(e) {
				keydownHandler(e);
			});

			return this;
		})
			.call({
				registerHandler: function(handler) {
					observer.registerHandler(handler);
				},
				unregisterHandler: function(handler) {
					observer.unregisterHandler(handler);
				}
			});

		// ----------------------------------------------------
		function keydownHandler(e) {
			clearTimeout(timer);

			input += e ? e.keyCode : event.keyCode;

			timer = setTimeout(cleanup, 1000);

			if (input.length > pattern.length) {
				input = input.substr((input.length - pattern.length));
			}

			if (input === pattern) {
				console.log("Konami activated");
				observer.notifyAll();
				cleanup();
				e.preventDefault();
			}
		}

		function cleanup() {
			clearTimeout(timer);
			input = '';
		}
	}

})(this);
(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$location', ['$observer', locationModuleFactory], false);

	function locationModuleFactory($observer) {

		return (function () {

			var self = $observer.create(this);

			/*
			* Listen to change scroll event
			*/
			window.addEventListener(
				'hashchange',
				function () {
					self.notifyAll(getAnchor());
				},
				false);

			return this;

		}).call({
			getAnchor: function () {
				return getAnchor();
			},
			get: function () {
				return getAnchor();
			}, 
			set: function(anchor) {
				window.location.hash = '#' + anchor;
			},
			setWhithoutMove: function(anchor) {
				if (history.pushState) {
					// IE10, Firefox, Chrome, etc.
					window.history.pushState(null, null, '#' + anchor);
				} else {
					// IE9, IE8, etc
					window.location.hash = '#' + anchor;
				}
			}
		});

		//-----------------------------------------------------

		function getAnchor() {
			return window.location.hash.split('#')[1];
		}
	}
})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}
	
	ctx.bambo.module('$nyan', nyanModuleFactory, isFirstApril());
	
	function nyanModuleFactory () {
		
		var images = [
			'http://rubeck.christophe.free.fr/img/nyancat.gif',
			'http://rubeck.christophe.free.fr/img/starwars.png'
		];
			
		return {
			$final: function() {
				if(isFirstApril()) {
					nyanFactory(getRandomImage());
				} 
			},
			run: function() {
				nyanFactory(getRandomImage());
			}
		};

		function getRandomImage() {
			var idx = getRandomInt(0, images.length);
			return images[idx];
		}
	}

	function nyanFactory(IMG_SRC) {

		var STEP_SIZE = 25;
		var body, img, targetX, targetY, mouseX = 0, mouseY = 0;

		body = document.getElementsByTagName('body')[0];

		createImgElement();
		body.appendChild(img);

		randomWalk();
		
		//-----------------------------------------------------------
		function createImgElement() {
			img = document.createElement('img');
			img.src = IMG_SRC;
			img.style.width = '200px';
			img.style.zIndex = '100';
			img.style.position = 'fixed';
			img.style.left = 0;
			img.style.top = 0;
		}

		function randomWalk() {
			setRandomTarget();
			setInterval(function () {
				if (atTarget()) {
					setRandomTarget()
				}
				stepTowardsTarget();
			}, 80);
		}

		function speed() {
			var bonus = 0;
			var dx = mouseX - posX();
			var dy = mouseY - posY();
			var dist = Math.sqrt(dx * dx + dy * dy);
			if (dist < 500) {
				bonus = (500 - dist) / 10;
			}
			return STEP_SIZE + bonus;
		}

		function atTarget() {
			return posX() == targetX && posY() == targetY;
		}

		function setRandomTarget() {
			targetX = Math.floor(Math.random() * window.innerWidth);
			targetY = Math.floor(Math.random() * window.innerHeight);
		}

		function posX() {
			return parseFloat(img.style.left);
		}

		function posY() {
			return parseFloat(img.style.top);
		}

		function stepTowardsTarget() {
			var dx = targetX - posX();
			var dy = targetY - posY();
			var d = Math.sqrt(dx * dx + dy * dy);
			var step = speed();
			if (d <= step) {
				img.style.left = targetX + 'px';
				img.style.top = targetY + 'px';
			}
			else {
				img.style.left = posX() + dx * step / d + 'px';
				img.style.top = posY() + dy * step / d + 'px';

				if (dx >= 0) {
					img.style.transform = "scaleX(1)";
				}
				else {
					img.style.transform = "scaleX(-1)";
				}
			}
		}
	}
	
	function isFirstApril() {
		var today = new Date(Date.now());
		return today.getDate() === 1 && today.getMonth() === 3;
	}

	function getRandomInt(min, max) {
		min = Math.ceil(min);
		max = Math.floor(max);
		return Math.floor(Math.random() * (max - min)) + min;
	  }

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$observer', observerModuleFactory, false);
	
	var isFunction = ctx.bambo.isFunction;
	var forEach = ctx.bambo.forEach;

	function observerModuleFactory() {

		return {
			create: function (obj) {
				return observerFactory(obj);
			}
		}
	}

	function observerFactory(obj) {

		var actionHandlers = [];

		return (function () {

			this.registerHandler = function (handler) {
				registerHandler(handler);
			};
			this.unregisterHandler = function (handler) {
				unregisterHandler(handler);
			};
			this.notifyAll = function () {
				notifyAll.apply(this, arguments);
			};

			return this;
		})
			.call(obj || {});

		//---------------------------------------------

		function registerHandler(handler) {

			if (isFunction(handler)) {
				actionHandlers.push(handler);
			}
			else {
				throw new Error('Handler must be a function');
			}
		}

		function unregisterHandler(handler) {

			if (isFunction(handler)) {
				actionHandlers = actionHandlers.filter(function (hl) {
					return hl !== handler;
				});
			}
			else {
				throw new Error('Handler must be a function');
			}
		}

		function notifyAll() {
			var args = arguments;

			forEach(actionHandlers, function (ah) {
				if (isFunction(ah)) {
					ah.apply(this, args);
				}
			});
		}
	}

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$scroll', ['$observer', scrollModuleFactory], false);

	function scrollModuleFactory($observer) {

		return (function () {

			var self = $observer.create(this);

			/*
			* Listen to change scroll event
			*/
			window.addEventListener(
				"scroll",
				(function () {
					return function () {
						self.notifyAll(scroll(), pageHeight(), screenHeight());
					};
				})(),
				false);

			return this;
		}).call({
			set: function (position) {
				setScroll(position);
			},
			get: function () {
				return scroll();
			},
			reset: function () {
				resetScroll();
			}
		});
	}

	function setScroll(position) {
		window.document.body.scrollTop = position;
		window.document.documentElement.scrollTop = position;
	}

	function resetScroll() {
		setScroll(0);
	}

	function screenHeight() {
		return window.innerHeight
			|| document.documentElement.clientHeight
			|| document.body.clientHeight;
	}

	function pageHeight() {
		var body = document.body,
			html = document.documentElement;

		return Math.max(body.scrollHeight, body.offsetHeight,
			html.clientHeight, html.scrollHeight, html.offsetHeight);
	}

	function scroll() {
		return window.scrollY || window.pageYOffset;
	}

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$dom', domModuleFactory, false);

	var forEach = ctx.bambo.forEach;

	function domModuleFactory() {

		return {
			select: function (selector) {
				return select(document, selector);
			},
			createElement: function (elementType) {
				return createElement(elementType);
			},
			createElementFromHTML: function (htmlElement) {
				return elementFactory(htmlElement);
			},
			createElementCollection: function () {
				return elementCollectionFactory();
			}
		};
	}

	function select(element, selector) {

		if (/\#(.*)/.test(selector)) {
			var id = /\#(.*)/.exec(selector)[1];
			return elementFactory(element.getElementById(id));
		}
		else if (/\.(.*)/.test(selector)) {
			var className = /\.(.*)/.exec(selector)[1];
			return elementCollectionFromHTML(element.getElementsByClassName(className));
		}

		return elementCollectionFromHTML(element.getElementsByTagName(selector));
	}

	function createElement(elementType) {
		return elementFactory(document.createElement(elementType));
	}

	function elementFactory(htmlElement) {

		var display;

		return {

			nativeElement: htmlElement,

			id: function() {
				return htmlElement.id;
			},

			select: function(selector) {
				return select(htmlElement, selector);
			},

			appendToParent: function (parentElement) {
				parentElement.nativeElement.appendChild(htmlElement);
				return this;
			},

			css: function (property, value) {
				htmlElement.style[property] = value;
				return this;
			},

			hide: function () {
				if (htmlElement.style.display !== 'none') {
					display = htmlElement.style.display;
					htmlElement.style.display = 'none';
				}
				return this;
			},

			show: function () {
				if (typeof display === 'string') {
					if (htmlElement.style.display === 'none') {
						htmlElement.style.display = display;
					}
				}
				else {
					htmlElement.style.display = 'initial';
				}
			},

			click: function (callback) {
				htmlElement.addEventListener('click', (function (ctx) {
					return function () {
						callback(ctx);
					};
				})(this));
				return this;
			},

			mouseover: function (callback) {
				htmlElement.addEventListener('mouseover', (function (ctx) {
					return function () {
						callback(ctx);
					};
				})(this));
				return this;
			},

			mouseleave: function (callback) {
				htmlElement.addEventListener('mouseleave', (function (ctx) {
					return function () {
						callback(ctx);
					};
				})(this));
				return this;
			},

			hasClass: function (className) {
				return htmlElement.classList.contains(className);
			},

			addClass: function (className) {
				if (!htmlElement.classList.contains(className)) {
					htmlElement.classList.add(className);
				}
				return this;
			},

			removeClass: function (className) {
				if (htmlElement.classList.contains(className)) {
					htmlElement.classList.remove(className);
				}
				return this;
			},

			text: function (text) {
				htmlElement.innerText = text;
				return this;
			},

			html: function(html) {
				htmlElement.innerHtml = html;
				return this;
			},

			offsetTop: function() {
				return htmlElement.offsetTop;
			},

			offsetBottom: function() {
				return htmlElement.offsetTop + htmlElement.clientHeight;
			},

			attribute: function(name) {
				if(htmlElement.hasAttribute(name)){
					return htmlElement.getAttribute(name);
				}
				return null;
			}
		};
	}

	function elementCollectionFromHTML(htmlElements) {

		var elements = [];

		forEach(htmlElements, function (htmlElement) {
			elements.push(elementFactory(htmlElement));
		})

		return elementCollectionFactory(elements);
	}

	function elementCollectionFactory(elements) {

		var elements = elements || [];

		return {

			add: function (element) {
				elements.push(element);
				return this;
			},

			css: function (property, value) {
				forEach(elements, function (element) {
					element.css(property, value);
				})
				return this;
			},

			hide: function () {
				forEach(elements, function (element) {
					element.hide();
				})
				return this;
			},

			show: function () {
				forEach(elements, function (element) {
					element.show();
				})
				return this;
			},

			click: function (callback) {
				forEach(elements, function (element) {
					element.click(callback);
				})
				return this;
			},

			addClass: function (className) {
				forEach(elements, function (element) {
					element.addClass(className);
				})
				return this;
			},

			removeClass: function (className) {
				forEach(elements, function (element) {
					element.removeClass(className);
				})
				return this;
			},

			first: function () {
				return elements[0];
			},

			forEach: function (callback) {
				forEach(elements, function (element, idx) {
					callback(element, idx);
				});
			},

			filter: function (callback) {

				var filtered = [];

				forEach(elements, function (element, idx) {
					if (callback(element, idx)) {
						filtered.push(element);
					}
				});

				return elementCollectionFactory(filtered);
			},

			count: function() {
				return elements.length;
			}
		};
	}

})(this);

(function (ctx) {
	'use strict';

	if (!ctx.hasOwnProperty('bambo')) {
		throw new Error('Library BamboJS not found !');
	}

	ctx.bambo.module('$leet', ['$dom', leetModuleFactory], false);

	function leetModuleFactory($dom) {

		var rootNode;

		var alphabets = {
			a: "@",
			b: "ß",
			c: "©",
			e: "ε",
			i: "1",
			l: '|',
			o: "0",
			r: "®",
		};

		return {
			$init: function () {
				rootNode = $dom.select('body').first();
			},
			run: function () {
				discoverDOM(rootNode.nativeElement, changeLetters);
			}
		}

		// -------------------------------------------
		function discoverDOM(elem, callback) {

			callback(elem);

			for (var i = 0, l = elem.children.length; i < l; i++) {
				discoverDOM(elem.children[i], callback);
			}
		}

		function changeLetters(elem) {

			if (elem.children.length === 0) {

				var text = elem.innerText;

				for (var i = 0; i < text.length; i++) {
					if (alphabets[text[i]]) {
						text = text.replace(text[i], alphabets[text[i]]);
					}
				}

				elem.innerText = text;
			}
		}
	}
})(this);
