import { motion } from 'framer-motion';
import { Box } from '@mui/material';

/**
 * PageTransition — wraps every page
 * @see Section 7 — Animation Rules
 */
const pageVariants = {
    initial: {
        opacity: 0,
        y: 10,
    },
    in: {
        opacity: 1,
        y: 0,
    },
    out: {
        opacity: 0,
        y: -10,
    }
};

const pageTransition = {
    type: 'tween',
    ease: 'easeInOut',
    duration: 0.25
};

const PageTransition = ({ children }) => {
    return (
        <motion.div
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
            style={{ width: '100%', height: '100%' }}
        >
            <Box sx={{ width: '100%', height: '100%' }}>
                {children}
            </Box>
        </motion.div>
    );
};

export default PageTransition;
