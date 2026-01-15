from flask import Flask, jsonify
import requests
import os
import logging
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MeTube configuration from environment variables
METUBE_URL = os.environ.get('METUBE_URL', 'http://metube:8081')
CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutes default

# Stats cache
_stats_cache = {
    'stats': None,
    'last_fetch': 0
}

def get_metube_stats():
    """Fetch statistics from MeTube API"""
    # Check cache first
    now = time.time()
    if (_stats_cache['stats'] and
        now - _stats_cache['last_fetch'] < CACHE_TIMEOUT):
        logger.info("Returning cached stats")
        return _stats_cache['stats']

    try:
        # Get history (queue, done, pending)
        history_response = requests.get(
            f'{METUBE_URL}/history',
            timeout=10
        )
        history_response.raise_for_status()
        history_data = history_response.json()

        # Get version info
        version_response = requests.get(
            f'{METUBE_URL}/version',
            timeout=10
        )
        version_response.raise_for_status()
        version_data = version_response.json()

        # Calculate statistics
        queue = history_data.get('queue', [])
        done = history_data.get('done', [])
        pending = history_data.get('pending', [])

        active_downloads = len(queue)
        completed_downloads = len(done)
        pending_downloads = len(pending)
        total_downloads = active_downloads + completed_downloads + pending_downloads

        # Get version info
        yt_dlp_version = version_data.get('yt-dlp', 'unknown')
        metube_version = version_data.get('MeTube', 'unknown')

        result = {
            'active_downloads': active_downloads,
            'completed_downloads': completed_downloads,
            'pending_downloads': pending_downloads,
            'total_downloads': total_downloads,
            'yt_dlp_version': yt_dlp_version,
            'metube_version': metube_version
        }

        # Update cache
        _stats_cache['stats'] = result
        _stats_cache['last_fetch'] = now

        logger.info(f"Fetched stats: {result}")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching MeTube stats: {e}")
        raise

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return 'OK', 200

@app.route('/stats', methods=['GET'])
def stats():
    """Get MeTube statistics"""
    try:
        stats_data = get_metube_stats()
        return jsonify(stats_data), 200
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching MeTube stats: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
