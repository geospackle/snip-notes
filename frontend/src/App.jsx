import { useState, useEffect } from 'react'
import './App.css'
import Auth from './Auth'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState(null)
  const [userEmail, setUserEmail] = useState(null)
  const [content, setContent] = useState('')
  const [searchTag, setSearchTag] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', text: '' })
  const [pendingResource, setPendingResource] = useState(null)
  const [editableTags, setEditableTags] = useState([])
  const [editableDescription, setEditableDescription] = useState('')
  const [newTag, setNewTag] = useState('')
  const [showEditMode, setShowEditMode] = useState(false)

  useEffect(() => {
    // Check for existing token on mount
    const savedToken = localStorage.getItem('token')
    const savedEmail = localStorage.getItem('userEmail')
    if (savedToken && savedEmail) {
      setToken(savedToken)
      setUserEmail(savedEmail)
      setIsAuthenticated(true)
    }
  }, [])

  const handleAuthSuccess = (accessToken, email) => {
    setToken(accessToken)
    setUserEmail(email)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail')
    setToken(null)
    setUserEmail(null)
    setIsAuthenticated(false)
    setResults([])
    setContent('')
    setSearchTag('')
    setPendingResource(null)
    setMessage({ type: '', text: '' })
  }

  const addResource = async () => {
    if (!content.trim()) {
      setMessage({ type: 'error', text: 'Please enter a URL or text' })
      return
    }

    setLoading(true)
    setMessage({ type: 'loading', text: 'Analyzing... This may take a moment...' })

    try {
      const response = await fetch(`${API_BASE}/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content: content.trim() })
      })

      if (response.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please login again.' })
        setTimeout(handleLogout, 1500)
        return
      }

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to add resource')
      }

      const resource = await response.json()
      setPendingResource(resource)
      setEditableTags([...resource.tags])
      setEditableDescription(resource.description)
      setShowEditMode(false)
      setMessage({ type: '', text: '' })
      setContent('')
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const searchByTag = async () => {
    if (!searchTag.trim()) {
      setMessage({ type: 'error', text: 'Please enter a tag' })
      return
    }

    setLoading(true)
    setMessage({ type: 'loading', text: 'Searching...' })

    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ tag: searchTag.trim() })
      })

      if (response.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please login again.' })
        setTimeout(handleLogout, 1500)
        return
      }

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Search failed')
      }

      const resources = await response.json()
      setResults(resources)
      setMessage({ type: '', text: '' })

      if (resources.length === 0) {
        setMessage({ type: 'info', text: 'No resources found with this tag' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleSaveYes = () => {
    setResults([pendingResource])
    setMessage({ type: 'success', text: 'Resource added successfully!' })
    setPendingResource(null)
    setShowEditMode(false)
    setTimeout(() => setMessage({ type: '', text: '' }), 3000)
  }

  const handleSaveNo = () => {
    setShowEditMode(true)
  }

  const handleDiscardTag = (indexToRemove) => {
    setEditableTags(editableTags.filter((_, index) => index !== indexToRemove))
  }

  const handleAddTag = () => {
    if (!newTag.trim()) return
    if (editableTags.length >= 5) {
      setMessage({ type: 'error', text: 'Maximum 5 tags allowed' })
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
      return
    }
    if (editableTags.includes(newTag.trim())) {
      setMessage({ type: 'error', text: 'Tag already exists' })
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
      return
    }
    setEditableTags([...editableTags, newTag.trim()])
    setNewTag('')
  }

  const handleSaveEdited = async () => {
    if (editableTags.length === 0) {
      setMessage({ type: 'error', text: 'At least one tag is required' })
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: pendingResource.content,
          tags: editableTags,
          description: editableDescription.trim()
        })
      })

      if (response.status === 401) {
        setMessage({ type: 'error', text: 'Session expired. Please login again.' })
        setTimeout(handleLogout, 1500)
        return
      }

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to save resource')
      }

      const resource = await response.json()
      setResults([resource])
      setMessage({ type: 'success', text: 'Resource saved with custom edits!' })
      setPendingResource(null)
      setTimeout(() => setMessage({ type: '', text: '' }), 3000)
    } catch (error) {
      setMessage({ type: 'error', text: `Error: ${error.message}` })
    } finally {
      setLoading(false)
    }
  }

  const handleCancelEdit = () => {
    setPendingResource(null)
    setEditableTags([])
    setEditableDescription('')
    setNewTag('')
    setShowEditMode(false)
  }

  const handleKeyPress = (e, action) => {
    if (e.key === 'Enter' && (action === 'search' || (action === 'add' && e.ctrlKey))) {
      action === 'search' ? searchByTag() : addResource()
    }
  }

  if (!isAuthenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />
  }

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <div>
            <h1>Tag Notes</h1>
            <p className="subtitle">Automatically tag web links and text ideas to find them later</p>
          </div>
          <div className="user-info">
            <span className="user-email">{userEmail}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>

        <div className="divider"></div>

        <section className="section">
          <h2>Add Resource</h2>
          <div className="input-group">
            <label>Enter URL or Text:</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={(e) => handleKeyPress(e, 'add')}
              placeholder="https://example.com or your text idea..."
            />
          </div>
          <button onClick={addResource} disabled={loading}>
            Analyze & Tag
          </button>
          {message.text && message.type === 'loading' && (
            <div className="message loading">{message.text}</div>
          )}
          {message.text && message.type === 'success' && (
            <div className="message success">{message.text}</div>
          )}
          {message.text && message.type === 'error' && !loading && (
            <div className="message error">{message.text}</div>
          )}
        </section>

        {pendingResource && (
          <section className="section confirmation-dialog">
            <h2>Save Note?</h2>
            <div className="resource-preview">
              <span className="resource-type">{pendingResource.resource_type}</span>
              <div className="resource-content">
                {pendingResource.content.length > 150
                  ? pendingResource.content.substring(0, 150) + '...'
                  : pendingResource.content}
              </div>
              <div className="resource-description">{editableDescription}</div>
              <div className="tags">
                {editableTags.map((tag, idx) => (
                  <span key={idx} className="tag editable-tag">
                    {tag}
                    <button
                      className="tag-remove"
                      onClick={() => handleDiscardTag(idx)}
                      title="Remove tag"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {!showEditMode && (
              <div className="button-group">
                <button className="btn-yes" onClick={handleSaveYes}>
                  Yes
                </button>
                <button className="btn-no" onClick={handleSaveNo}>
                  No
                </button>
              </div>
            )}

            {showEditMode && (
              <div className="edit-section">
                <div className="input-group">
                  <label>Edit Description:</label>
                  <textarea
                    value={editableDescription}
                    onChange={(e) => setEditableDescription(e.target.value)}
                    placeholder="Enter description..."
                  />
                </div>

                <div className="input-group">
                  <label>Add Tags (max 5):</label>
                  <div className="tag-input-group">
                    <input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && handleAddTag()}
                      placeholder="Enter tag..."
                    />
                    <button
                      onClick={handleAddTag}
                      disabled={editableTags.length >= 5}
                    >
                      Add Tag
                    </button>
                  </div>
                  <div className="tag-count">
                    {editableTags.length} / 5 tags
                  </div>
                </div>

                <div className="button-group">
                  <button onClick={handleSaveEdited} disabled={loading}>
                    Save Changes
                  </button>
                  <button className="btn-cancel" onClick={handleCancelEdit}>
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </section>
        )}

        <div className="divider"></div>

        <section className="section">
          <h2>Search by Tag</h2>
          <div className="input-group">
            <label>Enter Tag:</label>
            <input
              type="text"
              value={searchTag}
              onChange={(e) => setSearchTag(e.target.value)}
              onKeyDown={(e) => handleKeyPress(e, 'search')}
              placeholder="e.g., python, machine-learning, tutorial"
            />
          </div>
          <button onClick={searchByTag} disabled={loading}>
            Search
          </button>
        </section>

        <section className="section">
          <h2>Results</h2>
          <div className="results">
            {results.length === 0 && !message.text && (
              <div className="empty-state">
                No results yet. Add some resources or search by tag.
              </div>
            )}
            {message.type === 'info' && (
              <div className="empty-state">{message.text}</div>
            )}
            {results.map((resource) => (
              <div key={resource.id} className="resource-card">
                <span className="resource-type">{resource.resource_type}</span>
                <div className="resource-content">
                  {resource.content.length > 150
                    ? resource.content.substring(0, 150) + '...'
                    : resource.content}
                </div>
                <div className="resource-description">{resource.description}</div>
                <div className="tags">
                  {resource.tags.map((tag, idx) => (
                    <span key={idx} className="tag">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default App
