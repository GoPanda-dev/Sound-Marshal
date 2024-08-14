document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('mp3');
    const playButton = document.getElementById('play');
    const overlay = document.querySelector('.overlay');
    const volumeControl = document.getElementById('volume');
    const toggleCanvasButton = document.getElementById('toggle-canvas');
    const canvasSection = document.querySelector('.canvas');

    let lastVolume = localStorage.getItem('audioVolume') ? parseFloat(localStorage.getItem('audioVolume')) : audioPlayer.volume;

    function loadLastPlayedTrack() {
        const lastTrackSrc = localStorage.getItem('trackSrc');
        const lastTrackArtist = localStorage.getItem('trackArtist');
        const lastTrackTitle = localStorage.getItem('trackTitle');
        const lastCoverImage = localStorage.getItem('coverImage');

        if (lastTrackSrc) {
            audioPlayer.src = lastTrackSrc;
            audioPlayer.load();

            // Update the track metadata
            document.querySelector('.track-artist').textContent = lastTrackArtist || '';
            document.querySelector('.track-name').textContent = lastTrackTitle || '';

            // Update the overlay background image
            if (lastCoverImage) {
                overlay.style.backgroundImage = `url(${lastCoverImage})`;
            } else {
                overlay.style.backgroundImage = ''; // Remove the background if no image is provided
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

                // Update the audio source
                audioPlayer.src = trackSrc;
                audioPlayer.load(); // Ensure the new track is loaded before attempting to play

                // Update the track metadata
                document.querySelector('.track-artist').textContent = trackArtist;
                document.querySelector('.track-name').textContent = trackTitle;

                // Update the overlay background image
                if (coverImage) {
                    overlay.style.backgroundImage = `url(${coverImage})`;
                } else {
                    overlay.style.backgroundImage = ''; // Remove the background if no image is provided
                }

                // Play the audio
                audioPlayer.play().then(() => {
                    playButton.setAttribute('playing', 'playing');
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    alert("Unable to play this track. Please check the audio format or URL.");
                });

                // Save the current track information to localStorage
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
            // Restore the volume when playing
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
        audioPlayer.volume = this.value / 100; // Adjust volume based on user input
        lastVolume = audioPlayer.volume; // Update lastVolume whenever the user changes the volume
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

    // Event delegation for AJAX navigation and form handling
    document.addEventListener('click', function (event) {
        const link = event.target.closest('a');
        const form = event.target.closest('form');

        if (link) {
            const url = link.getAttribute('href');
            if (url && url !== '#' && url !== 'javascript:void(0)') {
                event.preventDefault();
                fetch(url)
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newContent = doc.querySelector('main.container').innerHTML;
                        document.querySelector('main.container').innerHTML = newContent;

                        // Reinitialize play buttons for the new content
                        setupPlayButtons();
                    })
                    .catch(error => console.error('Error loading content:', error));
            }
        }

        if (form && !form.hasAttribute('data-no-ajax')) {
            // Allow forms with `data-no-ajax` attribute to submit normally
            event.preventDefault();
            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action') || window.location.href;

            fetch(actionUrl, {
                method: form.getAttribute('method') || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newContent = doc.querySelector('main.container').innerHTML;
                document.querySelector('main.container').innerHTML = newContent;

                // Reinitialize play buttons for the new content
                setupPlayButtons();
            })
            .catch(error => console.error('Error submitting form:', error));
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
                    const newContent = doc.querySelector('main.container').innerHTML;
                    document.querySelector('main.container').innerHTML = newContent;

                    setupPlayButtons();
                })
                .catch(error => console.error('Error loading search results:', error));
        });
    }

    loadLastPlayedTrack();
    setupPlayButtons();
});
