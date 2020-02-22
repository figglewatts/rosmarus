name: render_framebuffer
shaders:
    vertex: |
        #version 330 core

        layout (location = 0) in vec3 in_Pos;
        layout (location = 2) in vec2 in_UV;

        out vec2 TexCoords;

        void main()
        {
            gl_Position = vec4(in_Pos.x, in_Pos.y, 0.0, 1.0);
            TexCoords = in_UV;
        }
    fragment: |
        #version 330 core

        out vec4 out_FragColor;

        in vec2 TexCoords;

        uniform sampler2D FramebufferTexture;

        void main()
        {
            out_FragColor = texture(FramebufferTexture, TexCoords);
        }
