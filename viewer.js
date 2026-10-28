import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// ==========================================
// 1. INISIALISASI SCENE, CAMERA, DAN RENDERER
// ==========================================

const host = document.querySelector('#viewport');

const scene = new THREE.Scene();
scene.background = new THREE.Color('#e5eff1');

const camera = new THREE.PerspectiveCamera(40, 1, 0.03, 100);

const renderer = new THREE.WebGLRenderer({
    antialias: true
});

renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

host.prepend(renderer.domElement);

// ==========================================
// 2. KONTROL KAMERA
// ==========================================

const controls = new OrbitControls(camera, renderer.domElement);

controls.enableDamping = true;
controls.minDistance = 1.2;
controls.maxDistance = 22;
controls.maxPolarAngle = Math.PI * 0.91;
controls.autoRotateSpeed = 0.65;

// ==========================================
// 3. PENCAHAYAAN
// ==========================================

scene.add(
    new THREE.HemisphereLight(0xffffff, 0x7f9da6, 2.5)
);

const sun = new THREE.DirectionalLight(0xfff5e6, 3);

sun.position.set(-4, 9, 7);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);

Object.assign(sun.shadow.camera, {
    left: -6,
    right: 6,
    top: 7,
    bottom: -5,
    near: 0.1,
    far: 30
});

sun.shadow.bias = -0.0007;
sun.shadow.normalBias = 0.015;

scene.add(sun);

const fill = new THREE.DirectionalLight(0xc9ecff, 1.5);

fill.position.set(4, 4, 5);
scene.add(fill);

// ==========================================
// 4. LANTAI
// ==========================================

const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(120, 120),
    new THREE.MeshStandardMaterial({
        color: 0xe5eff1,
        roughness: 1
    })
);

floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.58;
floor.receiveShadow = true;

scene.add(floor);

// ==========================================
// 5. INFORMASI KOMPONEN
// ==========================================

const specs = {
    Water_Level_Aman: {
        title: 'Water level 1 · Aman',
        short: 'S1 · Aman',
        type: 'SENSOR / TINGKAT BAWAH',
        body: 'Sensor paling bawah mendeteksi air pada tingkat awal. Saat permukaan air menyentuh jalur sensornya, ESP32 membaca perubahan sinyal. Status tetap aman selama sensor waspada dan bahaya belum tersentuh.'
    },

    Water_Level_Waspada: {
        title: 'Water level 2 · Waspada',
        short: 'S2 · Waspada',
        type: 'SENSOR / TINGKAT TENGAH',
        body: 'Sensor tengah menjadi penanda bahwa air sudah naik ke tingkat waspada. Dalam simulasi, sentuhan air pada sensor ini mengaktifkan LED kuning sebagai peringatan dini.'
    },

    Water_Level_Bahaya: {
        title: 'Water level 3 · Bahaya',
        short: 'S3 · Bahaya',
        type: 'SENSOR / TINGKAT ATAS',
        body: 'Sensor paling atas mendeteksi tingkat bahaya. Saat tersentuh air, sistem menyalakan LED merah dan dapat memicu buzzer. Pada demo ini, alarm hanya ditunjukkan secara visual.'
    },

    Control_Box: {
        title: 'Kotak kontrol',
        short: 'Kotak kontrol',
        type: 'PELINDUNG / RUMAH ELEKTRONIK',
        body: 'Kotak di bagian atas menampung ESP32 dan modul ultrasonik. Tiga LED dan buzzer berada pada panel depannya. Dasar kotak memiliki dua lubang bulat untuk kedua transduser ultrasonik. Tutup dapat dibuka untuk melihat isi.'
    },

    ESP32: {
        title: 'ESP32',
        short: 'ESP32',
        type: 'PENGENDALI / IoT',
        body: 'ESP32 membaca ketiga water level sensor, rain sensor, dan ultrasonik, lalu menentukan keluaran LED serta buzzer. Pada implementasi IoT, data dapat dikirim ke platform melalui Wi-Fi. Koneksi nyata belum diaktifkan pada demo ini.'
    },

    Rain_Sensor: {
        title: 'Rain sensor',
        short: 'Rain sensor',
        type: 'SENSOR / DETEKSI HUJAN',
        body: 'Papan sensor hujan dipasang terbuka di atas kotak dan sedikit miring agar terkena tetesan hujan. Permukaan konduktifnya mendeteksi kondisi basah. Papan ini tidak secara langsung mengukur curah hujan dalam milimeter.'
    },

    Ultrasonic: {
        title: 'Sensor ultrasonik',
        short: 'Ultrasonik',
        type: 'SENSOR / JARAK PERMUKAAN AIR',
        body: 'Modul berada di dalam kotak dengan dua lingkaran transduser menghadap ke bawah melalui dua lubang pada dasar kotak. Jarak ke permukaan air dapat digunakan untuk memperkirakan tinggi air. Pilih “Lihat dua lubang” untuk memeriksa bagian bawah.'
    },

    LED_Aman: {
        title: 'LED hijau · Aman',
        short: 'LED hijau',
        type: 'AKTUATOR / INDIKATOR AMAN',
        body: 'LED hijau menyala ketika air belum mencapai sensor tingkat waspada. Dalam demo, indikator mengikuti slider tinggi air.'
    },

    LED_Waspada: {
        title: 'LED kuning · Waspada',
        short: 'LED kuning',
        type: 'AKTUATOR / PERINGATAN DINI',
        body: 'LED kuning menyala ketika air menyentuh sensor tengah tetapi belum mencapai sensor atas. Ini menandai status waspada.'
    },

    LED_Bahaya: {
        title: 'LED merah · Bahaya',
        short: 'LED merah',
        type: 'AKTUATOR / PERINGATAN BAHAYA',
        body: 'LED merah menyala ketika air mencapai sensor tingkat atas. Indikator berkedip dalam simulasi untuk menandai status bahaya.'
    },

    Buzzer: {
        title: 'Buzzer',
        short: 'Buzzer',
        type: 'AKTUATOR / ALARM SUARA',
        body: 'Buzzer dipasang pada panel kotak. Pada alat nyata, komponen ini memberikan peringatan suara saat kondisi bahaya. Demo menggunakan animasi gelombang sebagai penanda alarm, tanpa memutar suara.'
    }
};

// ==========================================
// 6. STATE DAN REFERENSI KOMPONEN
// ==========================================

let model;
let selected = null;
let selectedKey = null;
let doorOpen = false;
let tween = null;
let state = 0;

let waterCurrent = 0.375;
let waterTarget = 0.375;

const objects = {};
const animated = [];

const status = document.querySelector('#status');
const slider = document.querySelector('#level');

const lights = [
    'LED_Aman',
    'LED_Waspada',
    'LED_Bahaya'
];

const sensors = [
    'Water_Level_Aman',
    'Water_Level_Waspada',
    'Water_Level_Bahaya'
];

// ==========================================
// 7. EFEK SENSOR ULTRASONIK
// ==========================================

const beamMaterial = new THREE.MeshBasicMaterial({
    color: 0x5ed5dd,
    transparent: true,
    opacity: 0.12,
    depthWrite: false,
    side: THREE.DoubleSide
});

const beam = new THREE.Mesh(
    new THREE.ConeGeometry(0.38, 1, 32, 1, true),
    beamMaterial
);

scene.add(beam);
beam.visible = false;

// ==========================================
// 8. EFEK GELOMBANG BUZZER
// ==========================================

const rings = [];

for (let i = 0; i < 3; i++) {
    const ring = new THREE.Mesh(
        new THREE.RingGeometry(0.12, 0.13, 48),
        new THREE.MeshBasicMaterial({
            color: 0xff7960,
            transparent: true,
            opacity: 0,
            depthWrite: false,
            side: THREE.DoubleSide
        })
    );

    scene.add(ring);
    rings.push(ring);
}

// ==========================================
// 9. FUNGSI PERGERAKAN KAMERA
// ==========================================

function moveCamera(target, position) {
    tween = {
        time: performance.now(),
        fromTarget: controls.target.clone(),
        fromPosition: camera.position.clone(),
        target: target.clone(),
        position: position.clone()
    };
}

function stopRotate() {
    controls.autoRotate = false;

    document.querySelector('#rotate').textContent =
        'Putar otomatis';

    document.querySelector('#rotate').setAttribute(
        'aria-pressed',
        'false'
    );
}

function overview(animate = true) {
    stopRotate();

    const target = new THREE.Vector3(0, 2.1, 0);
    const position = new THREE.Vector3(6.8, 5.3, 10.8);

    if (animate) {
        moveCamera(target, position);
    } else {
        controls.target.copy(target);
        camera.position.copy(position);
        controls.update();
    }
}

// ==========================================
// 10. MEMBUKA DAN MENUTUP KOTAK
// ==========================================

function setDoor(open) {
    doorOpen = open;

    const button = document.querySelector('#door');

    button.textContent = open
        ? 'Tutup kotak'
        : 'Buka kotak';

    button.setAttribute(
        'aria-pressed',
        String(open)
    );
}

// ==========================================
// 11. MEMILIH KOMPONEN 3D
// ==========================================

function select(key) {
    if (!objects[key]) return;

    stopRotate();

    selected = objects[key];
    selectedKey = key;

    const spec = specs[key];

    document.querySelector('#info-type').textContent =
        spec.type;

    document.querySelector('#info-title').textContent =
        spec.title;

    document.querySelector('#info-body').textContent =
        spec.body;

    const info = document.querySelector('#info');

    info.classList.remove('bump');

    void info.offsetWidth;

    info.classList.add('bump');

    document.querySelectorAll('[data-component]').forEach(
        button => {
            button.classList.toggle(
                'active',
                button.dataset.component === key
            );
        }
    );

    if (['ESP32', 'Ultrasonic', 'Control_Box'].includes(key)) {
        setDoor(true);
    }

    // Tutup panel untuk komponen aktuator di bagian depan.
    if ([...lights, 'Buzzer'].includes(key)) {
        setDoor(false);
    }

    let target = selected.getWorldPosition(
        new THREE.Vector3()
    );

    if ([...lights, 'Buzzer'].includes(key)) {
        const local = selected.position.clone();

        local.x -= 0.64;
        local.z += 0.43;

        target = objects.Control_Box.localToWorld(local);
    }

    const offset = new THREE.Vector3(1.6, 1.0, 3.6);

    if (key === 'Ultrasonic') {
        offset.set(1.3, -1.3, 2.3);
    }

    if (key === 'Rain_Sensor') {
        offset.set(1.2, 1.8, 2.5);
    }

    if (key === 'Control_Box') {
        offset.set(2, 1.2, 4);
    }

    moveCamera(
        target,
        target.clone().add(offset)
    );
}

// ==========================================
// 12. MEMBUAT TOMBOL KOMPONEN
// ==========================================

for (const [key, spec] of Object.entries(specs)) {
    const button = document.createElement('button');

    button.textContent = spec.short;
    button.dataset.component = key;
    button.onclick = () => select(key);

    document.querySelector('#components').append(button);
}

// ==========================================
// 13. MEMPERBARUI STATUS KETINGGIAN AIR
// ==========================================

function updateStatus() {
    const height = 0.24 + waterCurrent;

    const wet = [
        0.525,
        1.425,
        2.325
    ].map(level => height >= level);

    state = wet[2] ? 2 : wet[1] ? 1 : 0;

    status.textContent =
        ['AMAN', 'WASPADA', 'BAHAYA'][state] +
        ' · simulasi';

    status.style.background = [
        '#e0f4ea',
        '#fff0c3',
        '#ffe2df'
    ][state];

    status.style.color = [
        '#1d7852',
        '#91630b',
        '#b53f36'
    ][state];

    wet.forEach((isWet, index) => {
        const element = document.querySelector(
            `#wet${index}`
        );

        element.textContent =
            `S${index + 1}: ${
                isWet ? 'tersentuh air' : 'kering'
            }`;

        element.classList.toggle('wet', isWet);
    });
}

// ==========================================
// 14. KONTROL SLIDER KETINGGIAN AIR
// ==========================================

slider.oninput = () => {
    waterTarget = Number(slider.value) / 100 * 2.5;
};

document.querySelectorAll('[data-level]').forEach(button => {
    button.onclick = () => {
        slider.value = button.dataset.level;
        slider.oninput();
    };
});

// ==========================================
// 15. MEMUAT MODEL 3D GLB
// ==========================================

new GLTFLoader().load(
    './smart_flood.glb',

    gltf => {
        model = gltf.scene;

        model.traverse(object => {
            if (object.isMesh) {
                object.material = object.material.clone();

                object.castShadow = true;
                object.receiveShadow = true;

                animated.push(object);
            }
        });

        scene.add(model);

        for (const key of Object.keys(specs)) {
            objects[key] = model.getObjectByName(key);
        }

        model.getObjectByName('Water').traverse(object => {
            if (
                object.isMesh &&
                object.name === 'Water_Surface'
            ) {
                object.material.transparent = true;
                object.material.opacity = 0.70;
                object.material.depthWrite = false;
                object.castShadow = false;
            }
        });

        document.querySelector('#loading').hidden = true;

        slider.oninput();
        updateStatus();

        window.floodReady = true;
    },

    undefined,

    error => {
        document.querySelector('#loading').textContent =
            'Model gagal dimuat. Jalankan melalui server lokal sesuai README.';

        console.error(error);
    }
);

// ==========================================
// 16. TOMBOL TAMPILAN UTAMA
// ==========================================

document.querySelector('#overview').onclick = () => {
    selected = null;
    selectedKey = null;

    document.querySelectorAll('[data-component]').forEach(
        button => button.classList.remove('active')
    );

    setDoor(false);
    overview();

    document.querySelector('#info-type').textContent =
        'PROTOTYPE INTERAKTIF';

    document.querySelector('#info-title').textContent =
        'Kenali sistem Anda';

    document.querySelector('#info-body').textContent =
        'Pilih komponen 3D atau tombol untuk melihat fungsi dan animasinya.';
};

document.querySelector('#door').onclick = () => {
    setDoor(!doorOpen);
};

document.querySelector('#underside').onclick = () => {
    select('Ultrasonic');
    setDoor(false);

    const target = new THREE.Vector3(0, 3.18, 0.22);

    moveCamera(
        target,
        new THREE.Vector3(1.25, 1.8, 2.8)
    );
};

document.querySelector('#rotate').onclick = event => {
    tween = null;
    controls.autoRotate = !controls.autoRotate;

    event.target.textContent = controls.autoRotate
        ? 'Hentikan putaran'
        : 'Putar otomatis';

    event.target.setAttribute(
        'aria-pressed',
        String(controls.autoRotate)
    );
};

controls.addEventListener('start', () => {
    tween = null;
});

// ==========================================
// 17. INTERAKSI KLIK PADA MODEL 3D
// ==========================================

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

let down;

function getHit(event) {
    if (!model) return null;

    const rect = renderer.domElement.getBoundingClientRect();

    pointer.set(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
    );

    raycaster.setFromCamera(pointer, camera);

    const hits = raycaster.intersectObject(model, true);

    for (const hit of hits) {
        let object = hit.object;

        while (object && object !== model) {
            if (specs[object.name]) {
                return object.name;
            }

            object = object.parent;
        }

        if (
            hit.object.name !== 'Water_Surface' &&
            !hit.object.name.startsWith('Ripple')
        ) {
            return null;
        }
    }

    return null;
}

renderer.domElement.addEventListener('pointerdown', event => {
    down = [event.clientX, event.clientY];
});

renderer.domElement.addEventListener('pointerup', event => {
    if (
        event.button !== 0 ||
        !down ||
        Math.hypot(
            event.clientX - down[0],
            event.clientY - down[1]
        ) > 6
    ) {
        return;
    }

    const key = getHit(event);

    if (key) {
        select(key);
    }
});

renderer.domElement.addEventListener('pointermove', event => {
    renderer.domElement.style.cursor = getHit(event)
        ? 'pointer'
        : 'grab';
});

// ==========================================
// 18. RESPONSIVE RESIZE
// ==========================================

function resize() {
    const width = host.clientWidth;
    const height = host.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);
}

new ResizeObserver(resize).observe(host);

resize();
overview(false);

// ==========================================
// 19. ANIMASI UTAMA
// ==========================================

let previous = performance.now();

renderer.setAnimationLoop(now => {
    const dt = Math.min(
        (now - previous) / 1000,
        0.05
    );

    previous = now;

    const t = now / 1000;

    // Animasi perpindahan kamera.
    if (tween) {
        const progress = Math.min(
            (now - tween.time) / 900,
            1
        );

        const ease =
            progress * progress * (3 - 2 * progress);

        camera.position.lerpVectors(
            tween.fromPosition,
            tween.position,
            ease
        );

        controls.target.lerpVectors(
            tween.fromTarget,
            tween.target,
            ease
        );

        if (progress === 1) {
            tween = null;
        }
    }

    if (model) {
        // Animasi ketinggian air dan pintu kotak.
        waterCurrent = THREE.MathUtils.damp(
            waterCurrent,
            waterTarget,
            5,
            dt
        );

        model.getObjectByName('Water').position.y =
            waterCurrent;

        model.getObjectByName('Door_Hinge').rotation.y =
            THREE.MathUtils.damp(
                model.getObjectByName('Door_Hinge').rotation.y,
                doorOpen ? -Math.PI * 0.72 : 0,
                6,
                dt
            );

        updateStatus();

        // Efek cahaya pada komponen yang dipilih.
        for (const mesh of animated) {
            if (!mesh.material.emissive) continue;

            mesh.material.emissive.setHex(0x000000);
            mesh.material.emissiveIntensity = 0;

            let parent = mesh;
            let isSelected = false;

            while (parent) {
                if (parent === selected) {
                    isSelected = true;
                    break;
                }

                parent = parent.parent;
            }

            if (isSelected) {
                mesh.material.emissive.setHex(0x28c7b6);

                mesh.material.emissiveIntensity =
                    0.18 + 0.16 * (1 + Math.sin(t * 5));
            }
        }

        // Efek LED berdasarkan status air.
        lights.forEach((key, index) => {
            objects[key].traverse(object => {
                if (
                    object.isMesh &&
                    object.name.startsWith('LED_Lens')
                ) {
                    object.material.emissive.copy(
                        object.material.color
                    );

                    object.material.emissiveIntensity =
                        index === state
                            ? (
                                state === 2
                                    ? 1.2 + Math.sin(t * 7) * 0.8
                                    : 1.5
                            )
                            : 0.02;
                }
            });
        });

        // Animasi pancaran sensor ultrasonik.
        beam.visible = selectedKey === 'Ultrasonic';

        const distance = Math.max(
            0.05,
            3.06 - (0.24 + waterCurrent)
        );

        beam.position.set(
            0,
            3.06 - distance / 2,
            0.22
        );

        beam.scale.set(1, distance, 1);

        beam.material.opacity =
            0.09 + 0.05 * (1 + Math.sin(t * 4));

        // Animasi gelombang buzzer saat kondisi bahaya.
        const buzzer = objects.Buzzer;

        const buzzerPosition = buzzer.getWorldPosition(
            new THREE.Vector3()
        );

        const buzzerRotation = buzzer.getWorldQuaternion(
            new THREE.Quaternion()
        );

        rings.forEach((ring, index) => {
            ring.visible =
                state === 2 || selectedKey === 'Buzzer';

            ring.quaternion.copy(buzzerRotation);

            ring.position
                .copy(buzzerPosition)
                .add(
                    new THREE.Vector3(0, 0, 0.12)
                        .applyQuaternion(buzzerRotation)
                );

            const phase = (t * 0.75 + index / 3) % 1;

            ring.scale.setScalar(1 + phase * 2);
            ring.material.opacity = (1 - phase) * 0.65;
        });
    }

    controls.update();
    renderer.render(scene, camera);
});