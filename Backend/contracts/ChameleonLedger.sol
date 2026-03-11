// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ChameleonLedger
 * @author Chameleon Honeypot Project
 * @notice Gas-efficient on-chain anchoring of Merkle root hashes
 *         for tamper-proof honeypot log integrity verification.
 *
 * @dev    Each call to `storeMerkleRoot` appends a new root hash
 *         to a storage array and emits a `RootStored` event.
 *         The deployer is the only authorized caller (owner).
 *
 *         Deployed on Ethereum Sepolia Testnet.
 *
 * Gas Optimisation Notes:
 *   - Uses `string` instead of `bytes32` for human-readable SHA-256 hashes.
 *   - Minimal state writes (1 SSTORE per call).
 *   - No dynamic mapping — array-only for sequential access.
 *   - `onlyOwner` modifier avoids importing OpenZeppelin (saves deploy gas).
 */
contract ChameleonLedger {

    // ── State ───────────────────────────────────────────────────────────

    /// @notice Address that deployed the contract (only caller allowed).
    address public owner;

    /// @notice Ordered list of all anchored Merkle root hashes.
    string[] private _roots;

    // ── Events ──────────────────────────────────────────────────────────

    /// @notice Emitted every time a new Merkle root is stored.
    /// @param rootHash  SHA-256 Merkle root hash string (64 hex chars).
    /// @param timestamp Block timestamp at the moment of storage.
    /// @param index     Sequential index of this root in the array.
    event RootStored(
        string  rootHash,
        uint256 timestamp,
        uint256 index
    );

    // ── Modifiers ───────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "ChameleonLedger: caller is not owner");
        _;
    }

    // ── Constructor ─────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
    }

    // ── Write Functions ─────────────────────────────────────────────────

    /**
     * @notice Store a new Merkle root hash on-chain.
     * @dev    Only callable by the contract owner (backend service).
     *         Emits {RootStored} with the hash, block timestamp, and index.
     * @param _rootHash SHA-256 Merkle root hash (e.g. "a1b2c3d4e5...").
     */
    function storeMerkleRoot(string memory _rootHash) external onlyOwner {
        _roots.push(_rootHash);
        emit RootStored(_rootHash, block.timestamp, _roots.length - 1);
    }

    // ── View Functions ──────────────────────────────────────────────────

    /**
     * @notice Get the total number of stored Merkle roots.
     * @return count Number of roots stored.
     */
    function getRootCount() external view returns (uint256 count) {
        return _roots.length;
    }

    /**
     * @notice Retrieve a specific Merkle root by index.
     * @param index Zero-based index of the root.
     * @return rootHash The stored hash string.
     */
    function getRoot(uint256 index) external view returns (string memory rootHash) {
        require(index < _roots.length, "ChameleonLedger: index out of bounds");
        return _roots[index];
    }

    /**
     * @notice Get the most recently stored Merkle root.
     * @return rootHash The latest hash, or empty string if none stored.
     */
    function getLatestRoot() external view returns (string memory rootHash) {
        if (_roots.length == 0) return "";
        return _roots[_roots.length - 1];
    }
}
