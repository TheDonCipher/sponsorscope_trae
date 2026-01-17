# Platform Resistance User-Facing Messages

This document contains the user-facing copy and messaging for SponsorScope.ai's platform resistance system. These messages are designed to communicate access restrictions clearly and professionally while maintaining transparency about our anti-scraping measures.

## Message Categories

### 1. Platform Resistance (Scraper Detection)

**Primary Message:**
```
Access temporarily restricted due to automated activity detection. 
Please contact support@sponsorscope.ai for legitimate research access.
```

**Technical Details (collapsible):**
- Halt reason: [Specific detection reason]
- Halt timestamp: [ISO timestamp]
- Client IP: [IP address]
- Scraper guidance: Halt scraping operations. No fabricated data will be provided.
- Contact information: support@sponsorscope.ai
```

**Data Integrity Verdict:**
```
No fabricated data provided - scraper halted safely
```

### 2. Rate Limit Exceeded

**Primary Message:**
```
Rate limit exceeded. Please reduce request frequency or 
contact support@sponsorscope.ai for higher limits.
```

**Technical Details:**
- Remaining requests: [minute/hour/day counts]
- Retry after: 60 seconds
- Rate limit guidance: Reduce request frequency
```

### 3. Abuse Detection

**Primary Message:**
```
Request blocked due to suspicious activity.
```

**Technical Details:**
- Block reason: [Specific abuse reason]
- Detection method: [Pattern analysis/rapid resubmission/etc.]
```

### 4. Service Maintenance

**Primary Message:**
```
Service temporarily unavailable for maintenance.
Please try again later.
```

**Technical Details:**
- Retry after: 1 hour
- Maintenance type: [Read/Scan/Full]
```

### 5. Token Limit Reached

**Primary Message:**
```
Service temporarily unavailable due to resource constraints.
```

**Technical Details:**
- Resource type: AI processing tokens
- Retry after: 1 hour
- Estimated tokens needed: [token count]
```

## Message Design Principles

### Clarity
- Use plain language that non-technical users can understand
- Avoid jargon like "scraper," "bot detection," or technical implementation details
- Be specific about what the user should do next

### Transparency
- Provide technical details in collapsible sections for advanced users
- Include timestamps and relevant identifiers for debugging
- Explain why access is restricted without revealing sensitive detection methods

### Professional Tone
- Maintain a helpful, non-accusatory tone
- Focus on protecting the service rather than catching "bad actors"
- Offer clear paths to legitimate access

### Actionability
- Always provide a next step (contact support, retry later, etc.)
- Include specific contact information
- Give timeframes when applicable (retry after X seconds)

## Frontend Component Integration

### PlatformResistanceMessage Component

The React component displays messages with:
- **Visual hierarchy**: Icon + title + message
- **Contextual styling**: Different colors for different message types
- **Collapsible technical details**: For transparency without overwhelming users
- **Action buttons**: Retry and contact support options
- **Accessibility**: Proper ARIA labels and keyboard navigation

### usePlatformResistance Hook

The React hook provides:
- **Error detection**: Automatically identifies platform resistance errors
- **Type classification**: Categorizes errors for appropriate messaging
- **State management**: Tracks error state and provides reset functionality
- **Event handling**: Dispatches custom events for retry logic

## Error Handling Flow

1. **Detection**: System detects scraping behavior or policy violations
2. **Logging**: Comprehensive logging of the incident for analysis
3. **Response Generation**: Creates appropriate user-facing message
4. **Frontend Display**: Shows message with relevant details and actions
5. **User Guidance**: Provides clear next steps for legitimate users

## Contact Information

**Primary Support:**
- Email: support@sponsorscope.ai
- Response time: Within 24 hours for legitimate access requests

**Escalation:**
- For urgent research access: research@sponsorscope.ai
- For technical issues: tech@sponsorscope.ai

## Message Localization

Messages should be translatable for international users. Key phrases to localize:

- "Access temporarily restricted"
- "Rate limit exceeded"
- "Request blocked due to suspicious activity"
- "Service temporarily unavailable"
- "Contact support"
- "Try again later"

## Testing and Validation

### Message Testing
- Verify messages display correctly across different error scenarios
- Test collapsible sections function properly
- Ensure contact links work and reach appropriate destinations
- Validate that no sensitive information is exposed

### User Experience Testing
- Test with screen readers for accessibility
- Verify mobile responsiveness
- Check loading states and transitions
- Validate retry mechanisms work correctly

## Monitoring and Analytics

### Message Effectiveness
Track metrics such as:
- Contact support requests following resistance messages
- Retry attempts after rate limit messages
- User behavior changes after seeing messages
- False positive rates for legitimate users

### Message Optimization
Regularly review and update messages based on:
- User feedback and support ticket analysis
- Changes in scraping patterns and techniques
- Platform policy updates
- User experience research

## Security Considerations

### Information Disclosure
- Never reveal specific detection algorithms or thresholds
- Avoid exposing internal system architecture
- Don't provide information that could help bypass resistance
- Keep technical details minimal and high-level

### User Privacy
- Only display necessary client IP information
- Don't log or display sensitive user data
- Ensure compliance with privacy regulations
- Provide clear privacy policy links

## Implementation Notes

### Backend Integration
- Messages are generated in the platform resistance middleware
- Consistent formatting across all resistance types
- Proper HTTP status codes for each scenario
- Appropriate retry-after headers

### Frontend Integration
- Centralized message component for consistency
- Responsive design for all device types
- Loading states during retry attempts
- Error boundary protection for component failures

This messaging system ensures that platform resistance is communicated effectively while maintaining a positive user experience for legitimate users and providing clear guidance for those who need alternative access methods.