document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('mp3');
    const playButton = document.getElementById('play');
    const overlay = document.querySelector('.overlay');
    const volumeControl = document.getElementById('volume');
    const toggleCanvasButton = document.getElementById('toggle-canvas');
    const canvasSection = document.querySelector('.ToggleSection');

    let lastVolume = localStorage.getItem('audioVolume') ? parseFloat(localStorage.getItem('audioVolume')) : audioPlayer.volume;

    function loadLastPlayedTrack() {
        const lastTrackSrc = localStorage.getItem('trackSrc');
        const lastTrackArtist = localStorage.getItem('trackArtist');
        const lastTrackTitle = localStorage.getItem('trackTitle');
        const lastCoverImage = localStorage.getItem('coverImage');

        if (lastTrackSrc) {
            audioPlayer.src = lastTrackSrc;
            audioPlayer.load();

            document.querySelector('.track-artist').textContent = lastTrackArtist || '';
            document.querySelector('.track-name').textContent = lastTrackTitle || '';

            if (lastCoverImage) {
                overlay.style.backgroundImage = `url(${lastCoverImage})`;
            } else {
                overlay.style.backgroundImage = '';
            }

            if (localStorage.getItem('isPlaying') === 'true') {
                audioPlayer.play().then(() => {
                    playButton.setAttribute('playing', 'playing');
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    playButton.removeAttribute('playing');
                });
            } else {
                playButton.removeAttribute('playing');
            }
        } else {
            console.warn("No track info found in localStorage.");
            playButton.removeAttribute('playing');
        }
    }

    function setupPlayButtons() {
        document.querySelectorAll('.btn-play').forEach(function (button) {
            button.addEventListener('click', function () {
                const trackSrc = button.getAttribute('data-track-src');
                const trackArtist = button.getAttribute('data-track-artist');
                const trackTitle = button.getAttribute('data-track-title');
                const coverImage = button.getAttribute('data-cover');

                audioPlayer.src = trackSrc;
                audioPlayer.load();

                document.querySelector('.track-artist').textContent = trackArtist;
                document.querySelector('.track-name').textContent = trackTitle;

                if (coverImage) {
                    overlay.style.backgroundImage = `url(${coverImage})`;
                } else {
                    overlay.style.backgroundImage = '';
                }

                audioPlayer.play().then(() => {
                    playButton.setAttribute('playing', 'playing');
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    alert("Unable to play this track. Please check the audio format or URL.");
                });

                localStorage.setItem('trackSrc', trackSrc);
                localStorage.setItem('trackArtist', trackArtist);
                localStorage.setItem('trackTitle', trackTitle);
                localStorage.setItem('coverImage', coverImage);
                localStorage.setItem('isPlaying', 'true');
            });
        });
    }

    playButton.addEventListener('click', function () {
        if (audioPlayer.paused || audioPlayer.ended) {
            audioPlayer.volume = lastVolume;
            audioPlayer.play().then(() => {
                playButton.setAttribute('playing', 'playing');
                localStorage.setItem('isPlaying', 'true');
            }).catch(error => {
                console.error("Error playing audio:", error);
                alert("Unable to play this track. Please check the audio format or URL.");
            });
        } else {
            audioPlayer.pause();
            playButton.removeAttribute('playing');
            localStorage.setItem('isPlaying', 'false');
        }
    });

    audioPlayer.addEventListener('ended', function () {
        playButton.removeAttribute('playing');
        localStorage.setItem('isPlaying', 'false');
    });

    volumeControl.addEventListener('input', function () {
        audioPlayer.volume = this.value / 100;
        lastVolume = audioPlayer.volume;
        localStorage.setItem('audioVolume', lastVolume);
    });

    toggleCanvasButton.addEventListener('click', function () {
        if (canvasSection.style.display === 'none' || canvasSection.style.display === '') {
            canvasSection.style.display = 'block';
            toggleCanvasButton.classList.remove('collapsed');
        } else {
            canvasSection.style.display = 'none';
            toggleCanvasButton.classList.add('collapsed');
        }
    });

    document.addEventListener('click', function (event) {
        const link = event.target.closest('a');
        if (link) {
            const url = link.getAttribute('href');
            const noAjax = link.getAttribute('data-no-ajax');

            if (noAjax !== 'true' && url && url !== '#' && url !== 'javascript:void(0)') {
                event.preventDefault();
                fetch(url)
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newContent = doc.querySelector('main.container');
                        
                        if (newContent) {
                            document.querySelector('main.container').innerHTML = newContent.innerHTML;
                            setupPlayButtons();
                        } else {
                            window.location.href = url; // Fallback to full page load
                        }
                    })
                    .catch(error => {
                        console.error('Error loading content:', error);
                        window.location.href = url; // Fallback to full page load on error
                    });
            }
        }
    });

    const searchForm = document.querySelector('.navbar-search');
    if (searchForm) {
        searchForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(searchForm);
            const queryString = new URLSearchParams(formData).toString();
            const searchUrl = `${searchForm.action}?${queryString}`;

            fetch(searchUrl)
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const newContent = doc.querySelector('main.container');
                    
                    if (newContent) {
                        document.querySelector('main.container').innerHTML = newContent.innerHTML;
                        setupPlayButtons();
                    } else {
                        window.location.href = searchUrl; // Fallback to full page load
                    }
                })
                .catch(error => {
                    console.error('Error loading search results:', error);
                    window.location.href = searchUrl; // Fallback to full page load on error
                });
        });
    }

    loadLastPlayedTrack();
    setupPlayButtons();
});
