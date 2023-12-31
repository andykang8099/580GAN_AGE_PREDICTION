import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    def __init__(self, in_features):
        super(ResidualBlock, self).__init__()

        conv_block = [nn.ReflectionPad2d(1),
                      nn.Conv2d(in_features, in_features, 3),
                      nn.BatchNorm2d(in_features),
                      nn.ReLU(),
                      nn.ReflectionPad2d(1),
                      nn.Conv2d(in_features, in_features, 3),
                      nn.BatchNorm2d(in_features)]

        self.conv_block = nn.Sequential(*conv_block)

    def forward(self, x):
        return x + self.conv_block(x)


class Generator(nn.Module):
    def __init__(self, ngf, n_residual_blocks=9):
        super(Generator, self).__init__()

        model = [nn.ReflectionPad2d(3),
                 nn.Conv2d(3, ngf, 7),
                 nn.BatchNorm2d(ngf),
                 nn.ReLU()]

        in_features = ngf
        out_features = in_features * 2
        for _ in range(2):
            model += [nn.Conv2d(in_features, out_features, 3, stride=2, padding=1),
                      nn.BatchNorm2d(out_features),
                      nn.ReLU()]
            in_features = out_features
            out_features = in_features * 2

        for _ in range(n_residual_blocks):
            model += [ResidualBlock(in_features)]

        out_features = in_features // 2
        for _ in range(2):
            model += [nn.ConvTranspose2d(in_features, out_features, 3, stride=2, padding=1, output_padding=1),
                      nn.BatchNorm2d(out_features),
                      nn.ReLU()]
            in_features = out_features
            out_features = in_features // 2

        model += [nn.ReflectionPad2d(3),
                  nn.Conv2d(ngf, 3, 7),
                  nn.Tanh()]

        self.model = nn.Sequential(*model)

    def forward(self, x):
        return self.model(x)


class Discriminator(nn.Module):
    def __init__(self, ndf):
        super(Discriminator, self).__init__()

        model = [nn.Conv2d(3, ndf, 4, stride=2, padding=1),
                 nn.LeakyReLU(0.2, inplace=True)]

        model += [nn.Conv2d(ndf, ndf * 2, 4, stride=2, padding=1),
                  nn.BatchNorm2d(ndf * 2),
                  nn.LeakyReLU(0.2, inplace=True)]

        model += [nn.Conv2d(ndf * 2, ndf * 4, 4, stride=2, padding=1),
                  nn.InstanceNorm2d(ndf * 4),
                  nn.LeakyReLU(0.2, inplace=True)]

        model += [nn.Conv2d(ndf * 4, ndf * 8, 4, padding=1),
                  nn.InstanceNorm2d(ndf * 8),
                  nn.LeakyReLU(0.2, inplace=True)]

        model += [nn.Conv2d(ndf * 8, 1, 4, padding=1)]

        self.model = nn.Sequential(*model)

    def forward(self, x):
        x = self.model(x)
        return F.avg_pool2d(x, x.size()[2:]).view(x.size()[0], -1)