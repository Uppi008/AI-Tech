/* ==========================================================================
   AI Tech — Depth UI behaviour (3D depth · 4D motion · 5D interaction)
   - WebGL neural globe in the page hero (Three.js r128, optional)
   - Pointer-reactive card tilt with glare, magnetic buttons, mouse parallax
   - Scroll-driven hero parallax and progress bar
   Everything degrades gracefully: no WebGL, touch devices and
   prefers-reduced-motion all get a static but still layered UI.
   ========================================================================== */
(function () {
    'use strict';

    var root = document.documentElement;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    var HERO_SELECTOR = '.hero-section, .page-hero, .detail-hero, .project-hero';
    var TILT_SELECTOR = [
        '.service-card', '.support-card', '.category-card', '.project-card', '.stat-card',
        '.feature-card', '.team-card', '.industry-card', '.usecase-card', '.portfolio-card',
        '.result-card', '.related-card', '.feature-item-detail', '.nav-card',
        '.testimonial-card', '.highlights-card', '.tech-item'
    ].join(',');
    var MAGNETIC_SELECTOR = '.btn-gradient, .btn-light, .theme-toggle, .back-to-top, .social-icons a, .social-link';

    // Normalised pointer position, -1..1 on each axis
    var pointer = { x: 0, y: 0 };

    function cssVar(name, fallback) {
        var v = getComputedStyle(root).getPropertyValue(name).trim();
        return v || fallback;
    }

    function isDark() {
        return root.getAttribute('data-theme') === 'dark';
    }

    function clamp(v, min, max) {
        return Math.max(min, Math.min(max, v));
    }

    // Coalesce high-frequency events into one update per animation frame
    function perFrame(fn) {
        var queued = false;
        return function () {
            if (queued) return;
            queued = true;
            requestAnimationFrame(function () {
                queued = false;
                fn();
            });
        };
    }

    /* ---------------------------------------------------------------- 4D */
    function initScrollProgress() {
        var bar = document.createElement('div');
        bar.className = 'scroll-progress';
        bar.setAttribute('aria-hidden', 'true');
        document.body.appendChild(bar);

        var update = function () {
            var max = root.scrollHeight - window.innerHeight;
            bar.style.transform = 'scaleX(' + (max > 0 ? window.scrollY / max : 0).toFixed(4) + ')';
        };
        window.addEventListener('scroll', perFrame(update), { passive: true });
        window.addEventListener('resize', perFrame(update));
        update();
    }

    /* ---------------------------------------------------------------- 5D */
    function initTilt() {
        if (!finePointer || reduceMotion) return;

        document.querySelectorAll(TILT_SELECTOR).forEach(function (el) {
            // AOS owns the transform of elements it animates; leave those alone
            if (el.hasAttribute('data-aos')) return;
            el.classList.add('tilt');

            var max = 8;
            el.addEventListener('pointerenter', function () {
                // Wide cards tilt less so their far edges don't swing too much
                max = clamp(8 * 340 / el.offsetWidth, 3, 9);
                el.classList.add('tilt-active');
            });
            el.addEventListener('pointermove', function (e) {
                var r = el.getBoundingClientRect();
                var px = (e.clientX - r.left) / r.width;
                var py = (e.clientY - r.top) / r.height;
                el.style.setProperty('--rx', ((0.5 - py) * max * 2).toFixed(2) + 'deg');
                el.style.setProperty('--ry', ((px - 0.5) * max * 2).toFixed(2) + 'deg');
                el.style.setProperty('--mx', (px * 100).toFixed(1) + '%');
                el.style.setProperty('--my', (py * 100).toFixed(1) + '%');
            });
            el.addEventListener('pointerleave', function () {
                el.classList.remove('tilt-active');
                el.style.setProperty('--rx', '0deg');
                el.style.setProperty('--ry', '0deg');
            });
        });
    }

    function initMagnetic() {
        if (!finePointer || reduceMotion) return;

        document.querySelectorAll(MAGNETIC_SELECTOR).forEach(function (el) {
            el.addEventListener('pointermove', function (e) {
                var r = el.getBoundingClientRect();
                var dx = clamp((e.clientX - (r.left + r.width / 2)) * 0.25, -8, 8);
                var dy = clamp((e.clientY - (r.top + r.height / 2)) * 0.35, -6, 6);
                el.style.translate = dx.toFixed(1) + 'px ' + dy.toFixed(1) + 'px';
            });
            el.addEventListener('pointerleave', function () {
                el.style.translate = '';
            });
        });
    }

    function initPointerParallax() {
        var layers = document.querySelectorAll('[data-mouse-depth]');
        var visual = document.querySelector('.hero-visual');

        window.addEventListener('pointermove', function (e) {
            pointer.x = e.clientX / window.innerWidth * 2 - 1;
            pointer.y = e.clientY / window.innerHeight * 2 - 1;
        }, { passive: true });

        if (!finePointer || reduceMotion || (!layers.length && !visual)) return;

        window.addEventListener('pointermove', perFrame(function () {
            layers.forEach(function (el) {
                var d = parseFloat(el.getAttribute('data-mouse-depth')) || 1;
                el.style.translate = (pointer.x * d * 18).toFixed(1) + 'px ' + (pointer.y * d * 14).toFixed(1) + 'px';
            });
            if (visual) {
                visual.style.setProperty('--rx', (4 - pointer.y * 6).toFixed(2) + 'deg');
                visual.style.setProperty('--ry', (-10 + pointer.x * 10).toFixed(2) + 'deg');
            }
        }), { passive: true });
    }

    /* ------------------------------------------------------- hero (3D/4D) */
    function initHero() {
        var hero = document.querySelector(HERO_SELECTOR);
        if (!hero) return;

        hero.classList.add('depth-hero');

        var floor = document.createElement('div');
        floor.className = 'depth-floor';
        floor.setAttribute('aria-hidden', 'true');
        hero.insertBefore(floor, hero.firstChild);

        // Hero content drifts back and fades as the page scrolls away
        var content = hero.querySelector(':scope > .container');
        if (content && !reduceMotion) {
            var drift = function () {
                var h = hero.offsetHeight || 1;
                var y = Math.min(window.scrollY, h);
                content.style.translate = '0 ' + (y * 0.28).toFixed(1) + 'px';
                content.style.opacity = clamp(1 - (y / h) * 0.9, 0, 1).toFixed(3);
            };
            window.addEventListener('scroll', perFrame(drift), { passive: true });
            drift();
        }

        initNeuralScene(hero);
    }

    function initNeuralScene(hero) {
        var THREE = window.THREE;
        if (!THREE) return;

        var canvas = document.createElement('canvas');
        canvas.className = 'depth-canvas';
        canvas.setAttribute('aria-hidden', 'true');
        hero.insertBefore(canvas, hero.firstChild);

        var renderer;
        try {
            renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, powerPreference: 'low-power' });
        } catch (err) {
            canvas.remove();
            return;
        }
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        var small = window.innerWidth < 768;
        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
        camera.position.set(0, 0, 10);

        var rig = new THREE.Group();
        var globe = new THREE.Group();
        scene.add(rig);
        rig.add(globe);

        // Nodes spread evenly over a sphere (Fibonacci lattice), lightly jittered
        var N = small ? 140 : 240;
        var R = 3;
        var golden = Math.PI * (3 - Math.sqrt(5));
        var pos = new Float32Array(N * 3);
        for (var i = 0; i < N; i++) {
            var y = 1 - (i / (N - 1)) * 2;
            var ring = Math.sqrt(1 - y * y);
            var th = golden * i;
            var j = 1 + (Math.random() - 0.5) * 0.08;
            pos[i * 3] = Math.cos(th) * ring * R * j;
            pos[i * 3 + 1] = y * R * j;
            pos[i * 3 + 2] = Math.sin(th) * ring * R * j;
        }

        // Synapses between neighbouring nodes
        var spacing = Math.sqrt(4 * Math.PI * R * R / N);
        var maxD2 = Math.pow(spacing * 1.25, 2);
        var links = [];
        for (var a = 0; a < N; a++) {
            for (var b = a + 1; b < N; b++) {
                var dx = pos[a * 3] - pos[b * 3];
                var dy = pos[a * 3 + 1] - pos[b * 3 + 1];
                var dz = pos[a * 3 + 2] - pos[b * 3 + 2];
                if (dx * dx + dy * dy + dz * dz < maxD2) {
                    links.push(pos[a * 3], pos[a * 3 + 1], pos[a * 3 + 2], pos[b * 3], pos[b * 3 + 1], pos[b * 3 + 2]);
                }
            }
        }

        var nodeGeo = new THREE.BufferGeometry();
        nodeGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        var nodeMat = new THREE.PointsMaterial({ size: 0.07, transparent: true, depthWrite: false });
        globe.add(new THREE.Points(nodeGeo, nodeMat));

        var linkGeo = new THREE.BufferGeometry();
        linkGeo.setAttribute('position', new THREE.Float32BufferAttribute(links, 3));
        var linkMat = new THREE.LineBasicMaterial({ transparent: true, depthWrite: false });
        globe.add(new THREE.LineSegments(linkGeo, linkMat));

        // Pulsing wireframe core
        var coreMat = new THREE.MeshBasicMaterial({ wireframe: true, transparent: true });
        var core = new THREE.Mesh(new THREE.IcosahedronGeometry(1.25, 1), coreMat);
        rig.add(core);

        // Orbit rings carrying "data packets"
        var ringMat = new THREE.MeshBasicMaterial({ transparent: true });
        var ringA = new THREE.Mesh(new THREE.TorusGeometry(4.1, 0.012, 6, 180), ringMat);
        ringA.rotation.set(Math.PI * 0.42, 0.25, 0);
        var ringB = new THREE.Mesh(new THREE.TorusGeometry(4.6, 0.01, 6, 200), ringMat);
        ringB.rotation.set(Math.PI * 0.6, -0.5, 0);
        rig.add(ringA, ringB);

        var satMat = new THREE.MeshBasicMaterial();
        var satGeo = new THREE.SphereGeometry(0.08, 12, 12);
        var sats = [
            { ring: ringA, r: 4.1, speed: 0.5, phase: 0 },
            { ring: ringA, r: 4.1, speed: 0.5, phase: Math.PI },
            { ring: ringB, r: 4.6, speed: -0.35, phase: 1.2 }
        ];
        sats.forEach(function (s) {
            s.mesh = new THREE.Mesh(satGeo, satMat);
            s.ring.add(s.mesh);
        });

        // Ambient dust for parallax depth
        var D = small ? 150 : 350;
        var dpos = new Float32Array(D * 3);
        for (var k = 0; k < D; k++) {
            dpos[k * 3] = (Math.random() - 0.5) * 24;
            dpos[k * 3 + 1] = (Math.random() - 0.5) * 14;
            dpos[k * 3 + 2] = (Math.random() - 0.5) * 10 - 2;
        }
        var dustGeo = new THREE.BufferGeometry();
        dustGeo.setAttribute('position', new THREE.BufferAttribute(dpos, 3));
        var dustMat = new THREE.PointsMaterial({ size: 0.035, transparent: true, depthWrite: false });
        var dust = new THREE.Points(dustGeo, dustMat);
        scene.add(dust);

        function applyTheme() {
            var dark = isDark();
            var primary = new THREE.Color(cssVar('--primary-color', '#4361ee'));
            var accent = new THREE.Color(cssVar('--accent-color', '#4cc9f0'));
            var secondary = new THREE.Color(cssVar('--secondary-color', '#3a0ca3'));
            var main = dark ? accent : primary;

            nodeMat.color.copy(main);
            nodeMat.opacity = dark ? 0.95 : 0.8;
            linkMat.color.copy(dark ? primary.clone().lerp(accent, 0.5) : primary);
            linkMat.opacity = dark ? 0.28 : 0.2;
            coreMat.color.copy(dark ? accent : secondary);
            coreMat.opacity = dark ? 0.4 : 0.3;
            ringMat.color.copy(accent);
            ringMat.opacity = dark ? 0.45 : 0.4;
            satMat.color.copy(dark ? new THREE.Color('#ffffff') : primary);
            dustMat.color.copy(main);
            dustMat.opacity = dark ? 0.5 : 0.35;
        }

        var offsetX = parseFloat(hero.getAttribute('data-scene-x') || '0');
        var sceneScale = parseFloat(hero.getAttribute('data-scene-scale') || '1');

        function resize() {
            var w = hero.clientWidth;
            var h = hero.clientHeight;
            if (!w || !h) return;
            renderer.setSize(w, h, false);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();

            // Half of the visible width at the globe's depth, in world units
            var halfW = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2)) * 10 * camera.aspect;
            rig.position.x = w >= 992 ? offsetX * halfW : 0;
            rig.scale.setScalar(sceneScale * Math.min(1, halfW / 4.4));
        }

        var visible = true;
        var running = false;
        var scrollP = 0;
        var cur = { x: 0, y: 0 };
        var t0 = performance.now();

        function draw(now) {
            var t = (now - t0) / 1000;
            cur.x += (pointer.x - cur.x) * 0.04;
            cur.y += (pointer.y - cur.y) * 0.04;

            globe.rotation.y = t * 0.12 + cur.x * 0.5;
            globe.rotation.x = cur.y * 0.3 + scrollP * 0.9;
            core.rotation.set(-t * 0.25, -t * 0.18, 0);
            core.scale.setScalar(1 + Math.sin(t * 1.6) * 0.06);
            nodeMat.size = 0.07 * (1 + Math.sin(t * 2.2) * 0.18);
            ringA.rotation.z = t * 0.1;
            ringB.rotation.z = -t * 0.07;
            sats.forEach(function (s) {
                var ang = t * s.speed + s.phase;
                s.mesh.position.set(Math.cos(ang) * s.r, Math.sin(ang) * s.r, 0);
            });
            dust.rotation.y = t * 0.02 + cur.x * 0.12;
            dust.position.y = scrollP * 2;

            camera.position.x += (cur.x * 0.7 - camera.position.x) * 0.05;
            camera.position.y += (-cur.y * 0.45 - camera.position.y) * 0.05;
            camera.position.z = 10 + scrollP * 4;
            camera.lookAt(0, 0, 0);

            renderer.render(scene, camera);
        }

        function loop(now) {
            if (!visible || document.hidden) {
                running = false;
                return;
            }
            draw(now);
            requestAnimationFrame(loop);
        }

        function start() {
            if (running || reduceMotion) return;
            running = true;
            requestAnimationFrame(loop);
        }

        function renderStill() {
            draw(t0 + 4000);
        }

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (entries) {
                visible = entries[0].isIntersecting;
                if (visible) start();
            }).observe(hero);
        }
        document.addEventListener('visibilitychange', function () {
            if (!document.hidden) start();
        });
        window.addEventListener('scroll', perFrame(function () {
            scrollP = clamp(window.scrollY / (hero.offsetHeight || 1), 0, 1);
        }), { passive: true });
        window.addEventListener('resize', perFrame(function () {
            resize();
            if (reduceMotion) renderStill();
        }));
        new MutationObserver(function () {
            applyTheme();
            if (reduceMotion) renderStill();
        }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });

        applyTheme();
        resize();
        if (reduceMotion) {
            renderStill();
        } else {
            start();
        }
        requestAnimationFrame(function () {
            canvas.classList.add('is-ready');
        });
    }

    function init() {
        initScrollProgress();
        initPointerParallax();
        initHero();
        initTilt();
        initMagnetic();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
