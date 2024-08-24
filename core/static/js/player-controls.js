document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('mp3');
    const playButton = document.getElementById('play');
    const overlay = document.querySelector('.overlay');
    const volumeControl = document.getElementById('volume');
    const toggleCanvasButton = document.getElementById('toggle-canvas');
    const canvasSection = document.querySelector('.ToggleSection');

    const likeButton = document.getElementById('like');
    let currentTrackId = null;

    
    if (audioPlayer && playButton && overlay && volumeControl && toggleCanvasButton && canvasSection && likeButton) {

    let lastVolume = localStorage.getItem('audioVolume') ? parseFloat(localStorage.getItem('audioVolume')) : audioPlayer.volume;
    
    function loadLastPlayedTrack() {
        const lastTrackSrc = localStorage.getItem('trackSrc');
        const lastTrackArtist = localStorage.getItem('trackArtist');
        const lastTrackTitle = localStorage.getItem('trackTitle');
        const lastCoverImage = localStorage.getItem('coverImage');
        const lastTrackId = localStorage.getItem('trackId');
        const isPlaying = localStorage.getItem('isPlaying') === 'true'; 
        
        if (lastTrackSrc) {
            audioPlayer.src = lastTrackSrc;
            audioPlayer.load();
        
            document.querySelector('.track-artist').textContent = lastTrackArtist || '';
            document.querySelector('.track-name').textContent = lastTrackTitle || '';
            currentTrackId = lastTrackId;
        
            if (lastCoverImage) {
                overlay.style.backgroundImage = `url(${lastCoverImage})`;
            } else {
                overlay.style.backgroundImage = '';
            }
    
            checkIfTrackIsLiked(lastTrackId);
    
            if (isPlaying) {
                playButton.setAttribute('playing', 'playing');
            } else {
                playButton.removeAttribute('playing');
                localStorage.setItem('isPlaying', 'false');
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
                const trackId = button.getAttribute('data-track-id');  // Capture the track ID

                currentTrackId = trackId;  // Set currentTrackId

                // Store track details in localStorage
                localStorage.setItem('trackSrc', trackSrc);
                localStorage.setItem('trackArtist', trackArtist);
                localStorage.setItem('trackTitle', trackTitle);
                localStorage.setItem('coverImage', coverImage);
                localStorage.setItem('trackId', trackId);  // Store track ID in localStorage
                localStorage.setItem('isPlaying', 'false');

                // Update the audio player and play the track
                audioPlayer.src = trackSrc;
                audioPlayer.load();

                document.querySelector('.track-artist').textContent = trackArtist;
                document.querySelector('.track-name').textContent = trackTitle;

                if (coverImage) {
                    overlay.style.backgroundImage = `url(${coverImage})`;
                } else {
                    overlay.style.backgroundImage = '';
                }

                checkIfTrackIsLiked(trackId);  // Check if the track is liked

                audioPlayer.play().then(() => {
                    playButton.setAttribute('playing', 'playing');
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    alert("Unable to play this track. Please check the audio format or URL.");
                });
            });
        });
    }

    function checkIfTrackIsLiked(trackId) {
        if (trackId) {
            fetch(`/check-if-liked/${trackId}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_liked) {
                    likeButton.classList.add('liked');  // Indicate that the track is liked
                } else {
                    likeButton.classList.remove('liked');  // Indicate that the track is not liked
                }
            })
            .catch(error => console.error('Error checking if track is liked:', error));
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    likeButton.addEventListener('click', function () {
        if (currentTrackId) {
            fetch(`/toggle-like-track/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ track_id: currentTrackId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.liked) {
                        likeButton.classList.add('liked');  // Indicate that the track is liked
                    } else {
                        likeButton.classList.remove('liked');  // Indicate that the track is unliked
                    }
                } else {
                    console.error('Error toggling like:', data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('No current track ID is set.');
        }
    });

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
    }
});
