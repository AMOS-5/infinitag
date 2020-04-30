package com.amos.infinitag.services;

import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;
import java.util.stream.Stream;

import com.amos.infinitag.configuration.StorageProperties;
import com.amos.infinitag.exceptions.StorageException;
import com.amos.infinitag.exceptions.StorageFileNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.FileSystemUtils;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

@Service
public class FileSystemStorageService implements StorageService {

    private final Path rootLocation;

    @Autowired
    public FileSystemStorageService(StorageProperties properties) {
        this.rootLocation = Paths.get(properties.getLocation());
    }


    /**
     * Attempts to save a file using the local storage system
     * and returns the path of the saved file
     */
    @Override
    public String store(MultipartFile file, String name) {
        String originalFileName = file.getOriginalFilename();
        if (originalFileName != null) {
            String filename = StringUtils.cleanPath(originalFileName);
            try {
                if (file.isEmpty()) {
                    throw new StorageException("Failed to store empty file " + filename);
                }
                if (filename.contains("..")) {
                    throw new StorageException(
                        "Cannot store file with relative path outside current directory "
                            + filename);
                }
                try (InputStream inputStream = file.getInputStream()) {
                    Path path = this.rootLocation.resolve(name);
                    Files.copy(inputStream, path,
                        StandardCopyOption.REPLACE_EXISTING);

                    return path.toString();
                }
            }
            catch (IOException e) {
                throw new StorageException("Failed to store file " + filename, e);
            }
        }

        return "";
    }

    /**
     * @return A stream of paths on the local file system which have
     * been saved under the root location of the storage system.
     */
    @Override
    public Stream<Path> loadAll() {
        try {
            return Files.walk(this.rootLocation, 1)
                .filter(path -> !path.equals(this.rootLocation))
                .map(this.rootLocation::relativize);
        }
        catch (IOException e) {
            throw new StorageException("Failed to read stored files", e);
        }

    }

    /**
     * @param filename Name of the file to load
     * @return Path of the file on the storage system
     */
    @Override
    public Path load(String filename) {
        return rootLocation.resolve(filename);
    }

    /**
     *
     * @param filename Name of the file to load
     * @return Returns the file as a resource instead of a path
     */
    @Override
    public Resource loadAsResource(String filename) {
        try {
            Path file = load(filename);
            Resource resource = new UrlResource(file.toUri());
            if (resource.exists() || resource.isReadable()) {
                return resource;
            }
            else {
                throw new StorageFileNotFoundException("Could not read file: " + filename);

            }
        }
        catch (MalformedURLException e) {
            throw new StorageFileNotFoundException("Could not read file: " + filename, e);
        }
    }

    /**
     * Delete all the files under the root location
     */
    @Override
    public void deleteAll() {
        FileSystemUtils.deleteRecursively(rootLocation.toFile());
    }

    /**
     * Initializes the storage service by creating the directories necessary.
     */
    @Override
    public void init() {
        try {
            Files.createDirectories(rootLocation);
        }
        catch (IOException e) {
            throw new StorageException("Could not initialize storage", e);
        }
    }

    /**
     *
     * @param file MultipartFile to save. Will be given a UUID for a name.
     * @return Returns the path of the file on the file system.
     */
    @Override
    public String store(MultipartFile file) {
        UUID uuid = UUID.randomUUID();
        String name = uuid.toString();
        return this.store(file, name);
    }
}
