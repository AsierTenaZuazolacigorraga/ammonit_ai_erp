/**
 * Formats a UTC date string to local timezone in DD-MM-YYYY HH:mm:ss format
 * @param dateString - The date string to format (can be UTC, ISO, or database timestamp format)
 * @returns Formatted date string or "-" if date is null/undefined
 */
export const formatLocalDate = (dateString: string | null | undefined): string => {
    if (!dateString) {
        return "-";
    }
    try {
        // If dateString doesn't end with Z, it's likely a database timestamp format without timezone info
        // Ensure we treat it as UTC
        let parsedDate;

        if (dateString.endsWith('Z')) {
            // Already has UTC indicator
            parsedDate = new Date(dateString);
        } else if (dateString.includes('T')) {
            // ISO format without Z, add Z to explicitly mark as UTC
            parsedDate = new Date(dateString + 'Z');
        } else {
            // Database timestamp format (YYYY-MM-DD HH:MM:SS)
            // Convert to ISO format and mark as UTC
            parsedDate = new Date(dateString.replace(' ', 'T') + 'Z');
        }

        if (isNaN(parsedDate.getTime())) {
            console.error("Invalid date format:", dateString);
            return "Invalid Date";
        }

        // Get local date parts (parsedDate is already converted to local time by JavaScript)
        const day = String(parsedDate.getDate()).padStart(2, '0');
        const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
        const year = parsedDate.getFullYear();
        const hours = String(parsedDate.getHours()).padStart(2, '0');
        const minutes = String(parsedDate.getMinutes()).padStart(2, '0');
        const seconds = String(parsedDate.getSeconds()).padStart(2, '0');

        // Construct the desired format
        return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
    } catch (error) {
        console.error("Error formatting date:", error);
        return "Invalid Date";
    }
}; 