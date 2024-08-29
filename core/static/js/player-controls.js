document.addEventListener('DOMContentLoaded', function () {
    const audioPlayer = document.getElementById('mp3');
    const playButton = document.getElementById('play');
    const overlay = document.querySelector('.overlay');
    const volumeControl = document.getElementById('volume');
    const toggleCanvasButton = document.getElementById('toggle-canvas');
    const canvasSection = document.querySelector('.ToggleSection');
    const likeButton = document.getElementById('like');
    
    let currentTrackId = null;
    let lastVolume = localStorage.getItem('audioVolume') ? parseFloat(localStorage.getItem('audioVolume')) : audioPlayer.volume;

    const requiredElements = [audioPlayer, playButton, overlay, volumeControl, toggleCanvasButton, canvasSection, likeButton];
    if (requiredElements.some(el => !el)) {
        console.warn("Missing one or more required elements.");
        return;
    }

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
        
            overlay.style.backgroundImage = lastCoverImage ? `url(${lastCoverImage})` : '';
    
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
        document.querySelector('.track-list').addEventListener('click', function (event) {
            const button = event.target.closest('.btn-play');
            if (button) {
                const trackSrc = button.getAttribute('data-track-src');
                const trackArtist = button.getAttribute('data-track-artist');
                const trackTitle = button.getAttribute('data-track-title');
                const coverImage = button.getAttribute('data-cover');
                const trackId = button.getAttribute('data-track-id');
                
                currentTrackId = trackId;

                // Store track details in localStorage
                localStorage.setItem('trackSrc', trackSrc);
                localStorage.setItem('trackArtist', trackArtist);
                localStorage.setItem('trackTitle', trackTitle);
                localStorage.setItem('coverImage', coverImage);
                localStorage.setItem('trackId', trackId);
                localStorage.setItem('isPlaying', 'false');

                // Update the audio player and play the track
                audioPlayer.src = trackSrc;
                audioPlayer.load();

                document.querySelector('.track-artist').textContent = trackArtist;
                document.querySelector('.track-name').textContent = trackTitle;

                overlay.style.backgroundImage = coverImage ? `url(${coverImage})` : '';

                checkIfTrackIsLiked(trackId);

                audioPlayer.play().then(() => {
                    playButton.setAttribute('playing', 'playing');
                }).catch(error => {
                    console.error("Error playing audio:", error);
                    alert("Unable to play this track. Please check the audio format or URL.");
                });
            }
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
                    likeButton.classList.add('liked');
                } else {
                    likeButton.classList.remove('liked');
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
                    likeButton.classList.toggle('liked', data.liked);
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
        const isCollapsed = canvasSection.style.display === 'none' || canvasSection.style.display === '';
        canvasSection.style.display = isCollapsed ? 'block' : 'none';
        toggleCanvasButton.classList.toggle('collapsed', !isCollapsed);
    });

    document.addEventListener('click', function (event) {
        const link = event.target.closest('a');
        if (link) {
            const url = link.getAttribute('href');
            const noAjax = link.getAttribute('data-no-ajax');
    
            if (noAjax !== 'true' && url && url !== '#' && url !== 'javascript:void(0)') {
                event.preventDefault();

                try {
                    history.pushState(null, '', url);
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
                                window.location.href = url;
                            }
                        })
                        .catch(error => {
                            console.error('Error loading content:', error);
                            window.location.href = url;
                        });
                } catch (error) {
                    console.error('Error pushing state:', error);
                }
            }
        }
    });

    window.addEventListener('popstate', function(event) {
        const url = window.location.href;
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
                    window.location.href = url;
                }
            })
            .catch(error => {
                console.error('Error loading content:', error);
                window.location.href = url;
            });
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
                        window.location.href = searchUrl;
                    }
                })
                .catch(error => {
                    console.error('Error loading search results:', error);
                    window.location.href = searchUrl;
                });
        });
    }

    loadLastPlayedTrack();
    setupPlayButtons();
});
