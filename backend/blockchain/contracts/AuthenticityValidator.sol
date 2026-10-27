// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title AuthenticityValidator
 * @dev Cryptographic registry for verified academic documents.
 * Stores only immutable SHA-256 hashes, timestamps, and verification identifiers.
 */
contract AuthenticityValidator {
    struct VerificationRecord {
        string documentHash;
        string verificationId;
        string studentIdCode;
        string collegeCode;
        uint256 timestamp;
        bool isAuthenticated;
        address verifiedBy;
    }

    // Mapping from document hash to VerificationRecord
    mapping(string => VerificationRecord) private records;
    mapping(string => bool) private recordExists;

    event DocumentRecorded(
        string indexed documentHash,
        string verificationId,
        uint256 timestamp,
        bool isAuthenticated,
        address indexed recorder
    );

    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function recordVerification(
        string memory _documentHash,
        string memory _verificationId,
        string memory _studentIdCode,
        string memory _collegeCode,
        bool _isAuthenticated
    ) public {
        require(bytes(_documentHash).length > 0, "Document hash cannot be empty");
        require(bytes(_verificationId).length > 0, "Verification ID cannot be empty");

        records[_documentHash] = VerificationRecord({
            documentHash: _documentHash,
            verificationId: _verificationId,
            studentIdCode: _studentIdCode,
            collegeCode: _collegeCode,
            timestamp: block.timestamp,
            isAuthenticated: _isAuthenticated,
            verifiedBy: msg.sender
        });

        recordExists[_documentHash] = true;

        emit DocumentRecorded(
            _documentHash,
            _verificationId,
            block.timestamp,
            _isAuthenticated,
            msg.sender
        );
    }

    function getVerification(string memory _documentHash)
        public
        view
        returns (
            string memory documentHash,
            string memory verificationId,
            string memory studentIdCode,
            string memory collegeCode,
            uint256 timestamp,
            bool isAuthenticated,
            address verifiedBy
        )
    {
        require(recordExists[_documentHash], "Verification record does not exist on blockchain");
        VerificationRecord memory rec = records[_documentHash];
        return (
            rec.documentHash,
            rec.verificationId,
            rec.studentIdCode,
            rec.collegeCode,
            rec.timestamp,
            rec.isAuthenticated,
            rec.verifiedBy
        );
    }

    function isDocumentVerified(string memory _documentHash) public view returns (bool) {
        return recordExists[_documentHash] && records[_documentHash].isAuthenticated;
    }
}
